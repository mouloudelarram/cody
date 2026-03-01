from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
import requests
import json
import logging
import uuid
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=".")

OLLAMA_URL    = "http://localhost:11434"
DEFAULT_MODEL = "llama2:7b"
HISTORY_FILE  = "chat_history.json"


# ── History helpers ───────────────────────────────────────────────────────────

def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not read history file: {e}")
    return {}


def save_history(history: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Could not write history file: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/models", methods=["GET"])
def list_models():
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        res.raise_for_status()
        models = [m["name"] for m in res.json().get("models", [])]
        return jsonify({"models": models})
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to the AI backend."}), 503
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return jsonify({"error": "Failed to fetch models."}), 500


# ── Chat history CRUD ─────────────────────────────────────────────────────────

@app.route("/api/chats", methods=["GET"])
def get_chats():
    """Return all chat sessions (id, title, date) sorted newest first."""
    history = load_history()
    chats = [
        {
            "id":      cid,
            "title":   chat.get("title", "Untitled"),
            "model":   chat.get("model", ""),
            "updated": chat.get("updated", ""),
        }
        for cid, chat in history.items()
    ]
    chats.sort(key=lambda c: c["updated"], reverse=True)
    return jsonify({"chats": chats})


@app.route("/api/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    """Return full message list for one chat."""
    history = load_history()
    chat = history.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    return jsonify(chat)


@app.route("/api/chats", methods=["POST"])
def create_chat():
    """Create a new empty chat session."""
    data  = request.get_json(silent=True) or {}
    cid   = str(uuid.uuid4())
    now   = datetime.utcnow().isoformat()
    chat  = {
        "id":       cid,
        "title":    data.get("title", "New chat"),
        "model":    data.get("model", DEFAULT_MODEL),
        "created":  now,
        "updated":  now,
        "messages": [],
    }
    history = load_history()
    history[cid] = chat
    save_history(history)
    return jsonify(chat), 201


@app.route("/api/chats/<chat_id>", methods=["PATCH"])
def update_chat(chat_id):
    """Rename a chat."""
    history = load_history()
    if chat_id not in history:
        return jsonify({"error": "Chat not found."}), 404
    data = request.get_json(silent=True) or {}
    if "title" in data:
        history[chat_id]["title"]   = data["title"][:80]
        history[chat_id]["updated"] = datetime.utcnow().isoformat()
    save_history(history)
    return jsonify(history[chat_id])


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    """Delete a chat session."""
    history = load_history()
    if chat_id not in history:
        return jsonify({"error": "Chat not found."}), 404
    del history[chat_id]
    save_history(history)
    return jsonify({"deleted": chat_id})


# ── Ask (streaming) ───────────────────────────────────────────────────────────

@app.route("/api/chats/<chat_id>/ask", methods=["POST"])
def ask(chat_id):
    """Stream an AI response and persist both messages to the chat."""
    history = load_history()
    if chat_id not in history:
        return jsonify({"error": "Chat not found."}), 404

    data   = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    model  = (data.get("model")  or history[chat_id].get("model") or DEFAULT_MODEL).strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400
    if len(prompt) > 32_000:
        return jsonify({"error": "Prompt exceeds the 32 000 character limit."}), 400

    # Save user message immediately
    now = datetime.utcnow().isoformat()
    history[chat_id]["messages"].append({"role": "user", "content": prompt, "ts": now})
    history[chat_id]["updated"] = now
    history[chat_id]["model"]   = model

    # Auto-title from first message (first 60 chars)
    if len(history[chat_id]["messages"]) == 1:
        history[chat_id]["title"] = prompt[:60] + ("…" if len(prompt) > 60 else "")

    save_history(history)
    logger.info(f"Ask | chat={chat_id} model={model} prompt_len={len(prompt)}")

    full_response = []

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": True},
                stream=True,
                timeout=300,
            ) as r:
                if r.status_code != 200:
                    err = r.text or "Unknown error."
                    yield f"data: {json.dumps({'error': err})}\n\n"
                    return

                for raw_line in r.iter_lines():
                    if not raw_line:
                        continue
                    try:
                        chunk = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue

                    token = chunk.get("response", "")
                    done  = chunk.get("done", False)

                    if token:
                        full_response.append(token)
                        yield f"data: {json.dumps({'token': token})}\n\n"

                    if done:
                        # Persist AI reply
                        ai_text = "".join(full_response)
                        h2 = load_history()
                        if chat_id in h2:
                            h2[chat_id]["messages"].append({
                                "role": "assistant",
                                "content": ai_text,
                                "ts": datetime.utcnow().isoformat(),
                            })
                            h2[chat_id]["updated"] = datetime.utcnow().isoformat()
                            save_history(h2)
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        return

        except requests.exceptions.ConnectionError:
            yield f"data: {json.dumps({'error': 'Cannot connect to the AI backend.'})}\n\n"
        except requests.exceptions.Timeout:
            yield f"data: {json.dumps({'error': 'Request timed out.'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': 'An unexpected error occurred.'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
