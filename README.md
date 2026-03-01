# Cody AI 🤖

A self-hosted, privacy-first AI chat application that runs **entirely on your own machine**. No data ever leaves your server. Built with Python (Flask) on the backend and a clean, dark terminal-aesthetic frontend powered by [Ollama](https://ollama.com).

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat-square&logo=flask&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-c8f55a?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%2F%20Linux-E95420?style=flat-square&logo=ubuntu&logoColor=white)

---

## ✨ Features

- 🧠 **Multiple AI models** — switch between any model installed in Ollama (Llama 2, Mistral, CodeLlama, etc.)
- ⚡ **Real-time streaming** — responses stream token by token as the AI generates them
- 💾 **Persistent chat history** — all conversations saved locally to `chat_history.json`
- 🗂️ **Sidebar with chat management** — open, close, and delete past conversations
- ✍️ **Markdown rendering** — bold, italic, code blocks with copy buttons, lists, headings
- ⏹️ **Stop generation** — cancel a response mid-stream at any time
- 📱 **Mobile responsive** — works on phones and tablets
- 🔒 **100% private** — no cloud, no API keys, no telemetry

---

## 📸 Preview

```
┌─────────────────┬──────────────────────────────────────────┐
│  ● Chats    [+] │  llama2:7b · response stream             │
│─────────────────│                                          │
│ > Today         │  Ask Cody                                │
│   How does...   │  Your private AI assistant               │
│   Explain...    │                                          │
│   Python sort   │  ┌─────────────────────────────────────┐ │
│                 │  │ You                                 │ │
│                 │  │ Explain quantum computing           │ │
│                 │  ├─────────────────────────────────────┤ │
│                 │  │ Cody                                │ │
│                 │  │ Quantum computing uses qubits...▋  │ │
│                 │  └─────────────────────────────────────┘ │
│                 │  [Type your question here...]  [Send →]  │
└─────────────────┴──────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
Cody-ai/
├── app.py               # Flask backend — API routes, streaming, chat persistence
├── index.html           # Frontend — UI, markdown renderer, SSE client
├── chat_history.json    # Auto-created on first message — stores all conversations
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Ubuntu / Debian Linux
- Python 3.8+
- [Ollama](https://ollama.com) installed

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull a model

```bash
# Llama 2 (3.8 GB)
ollama pull llama2:7b

# Or try other models
ollama pull mistral        # faster, often better
ollama pull codellama      # optimised for code
ollama pull tinyllama      # lightweight, 637 MB
```

### 3. Clone the repo

```bash
git clone https://github.com/yourusername/Cody-ai.git
cd Cody-ai
```

### 4. Install Python dependencies

```bash
pip install flask requests
```

### 5. Start Ollama (keep this running)

```bash
ollama serve
```

### 6. Start the app

```bash
python app.py
```

### 7. Open in your browser

```
http://localhost:8080
```

---

## 🌐 Hosting on Your Network

To make the app accessible to other devices on your local network or via your public IP:

**Access from another device on your LAN:**
```bash
# Find your local IP
hostname -I
# Then visit http://YOUR_LOCAL_IP:8080 from any device
```

**Access via public IP (port forwarding required):**

1. Open port `8080` in your firewall:
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

2. Log into your router and add a port forwarding rule:
   - External port: `8080`
   - Internal IP: your machine's local IP
   - Internal port: `8080`
   - Protocol: TCP

3. Visit `http://YOUR_PUBLIC_IP:8080`

> **Tip:** For a stable public address, use a free dynamic DNS service like [DuckDNS](https://www.duckdns.org).

---

## 🔧 Configuration

All configuration is at the top of `app.py`:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `DEFAULT_MODEL` | `llama2:7b` | Model used if none selected |
| `HISTORY_FILE` | `chat_history.json` | Path to the chat history file |

To change the port, edit the last line of `app.py`:
```python
app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
```

---

## 🛠️ API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/models` | List all installed Ollama models |
| `GET` | `/api/chats` | List all chat sessions |
| `POST` | `/api/chats` | Create a new chat session |
| `GET` | `/api/chats/:id` | Get full message history for a chat |
| `PATCH` | `/api/chats/:id` | Rename a chat |
| `DELETE` | `/api/chats/:id` | Delete a chat |
| `POST` | `/api/chats/:id/ask` | Send a message and stream the response (SSE) |

---

## ▶️ Running in the Background

**Option 1 — nohup (simple):**
```bash
nohup python app.py &
```

**Option 2 — screen (recommended, lets you reattach):**
```bash
sudo apt install screen
screen -S Cody
python app.py
# Detach: Ctrl+A then D
# Reattach later: screen -r Cody
```

**Option 3 — systemd service (runs on boot):**

Create `/etc/systemd/system/Cody.service`:
```ini
[Unit]
Description=Cody AI
After=network.target

[Service]
WorkingDirectory=/path/to/Cody-ai
ExecStart=/usr/bin/python3 /path/to/Cody-ai/app.py
Restart=always
User=your-username

[Install]
WantedBy=multi-user.target
```

Then enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable Cody
sudo systemctl start Cody
```

---

## 🧩 Adding More Models

List what you have installed:
```bash
ollama list
```

Pull any model from the [Ollama library](https://ollama.com/library):
```bash
ollama pull <model-name>
```

The model selector in the UI updates automatically — no code changes needed.

---

## 📋 Requirements

```
flask>=3.0
requests>=2.31
```

Install with:
```bash
pip install flask requests
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.com) — for making local LLMs easy to run
- [Meta AI](https://ai.meta.com) — for the Llama 2 model
- [Mistral AI](https://mistral.ai) — for the Mistral model

---
# Cody v1 :
<img width="1899" height="868" alt="image" src="https://github.com/user-attachments/assets/8e6b365e-4b7e-4e61-bbd9-ca9232957e34" />
