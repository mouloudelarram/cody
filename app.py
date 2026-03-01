from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder=".")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt is empty"}), 400

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "llama2:7b", "prompt": prompt, "stream": False},
            timeout=120,
        )
        result = response.json()
        answer = result.get("response", "No response received.")
        return jsonify({"answer": answer})

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to Ollama. Make sure it's running: run 'ollama serve' in a terminal."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🦙 Llama 2 Web App running at http://localhost:5000")
    print("Make sure Ollama is running: ollama serve")
    app.run(host="0.0.0.0", port=5000, debug=True)
