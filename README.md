# ✦ AnikaAI — CV Builder Chatbot

A modern AI-powered desktop chatbot that reads your personal information and generates a professional CV — built with Python, Tkinter, and Ollama.



---

## ✨ Features

- 🤖 **AI-powered CV generation** — just type "Create my CV"
- 💬 **Ask questions about your CV** — "What are my skills?", "Where did I study?"
- 📄 **Auto-loads your info** — place a `.txt` file in the folder, it loads automatically
- 🔄 **Switch between files** — toggle between multiple CV info files
- 📥 **Export CV as PDF** — clean professional formatting
- 💾 **Persistent chat history** — saved across sessions
- 🔁 **Auto-starts Ollama** — no need to start Ollama manually
- ⚡ **Streaming responses** — words appear one by one like ChatGPT
- 🎨 **Dark modern UI** — ChatGPT-style sidebar with multiple chats
- 🔒 **100% local & private** — no data sent to the internet

---

## 🖥️ Preview

```
┌─────────────────────────────────────────────────┐
│ ✦ AnikaAI          │  Ask anything about your CV │
│                    │                             │
│ ＋ New Chat        │  AI: Your name is Anika,    │
│ 📄 Upload TXT      │  a Full Stack Developer...  │
│ 🔄 Switch File     │                             │
│ 📌 Using: info.txt │                             │
│ 📥 Export PDF      │  ┌─────────────────────┐   │
│                    │  │ Ask anything...   ↑ │   │
│ Model              │  └─────────────────────┘   │
│ [llama3.2:1b ▼]   │                             │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### 1. Install Ollama
Download from [https://ollama.com](https://ollama.com) and install it.

Then pull a model:
```bash
ollama pull llama3.2:1b
```

### 2. Clone the repo
```bash
git clone https://github.com/anika92/cv_genertaor_chatbot.git
cd cv_genertaor_chatbot
```

### 3. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install ollama fpdf2
```

### 5. Add your info file
Create an `info.txt` file in the project folder with your personal details:
```
Name: Your Name
Email: your@email.com
Phone: 01700000000
Location: Dhaka, Bangladesh
LinkedIn: linkedin.com/in/yourprofile
GitHub: github.com/yourusername

Summary:
Write a short summary about yourself here...

Education:
B.Sc. Computer Science — University Name (2018-2022)

Experience:
Job Title — Company Name (2022 - Present)
- What you did
- What you achieved

Skills:
Python, FastAPI, React, PostgreSQL, Docker

Projects:
Project Name — Brief description
```

### 6. Run the app
```bash
python main.py
```

---

## 💡 How to Use

| Action | What to do |
|---|---|
| Ask about your CV | Type any question e.g. "What are my skills?" |
| Generate full CV | Type "Create my CV" |
| Export as PDF | Click 📥 Export CV as PDF in sidebar |
| Upload new file | Click 📄 Upload TXT File |
| Switch files | Click 🔄 Switch File |
| Change AI model | Select from dropdown in sidebar |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core language |
| Tkinter | Desktop UI |
| Ollama | Local AI engine |
| fpdf2 | PDF export |

---

## 🤖 Supported Models

| Model | Size | Speed | Best For |
|---|---|---|---|
| `llama3.2:1b` | 1.3GB | ⚡ fastest | Quick answers |
| `llama3.2` | 2GB | fast | Balanced |
| `mistral` | 4GB | medium | ✅ Best quality |
| `glm-5.2:cloud` | cloud | ⚡⚡ | Cloud speed |
| `minimax-m3:cloud` | cloud | ⚡⚡ | Cloud speed |

Pull any model:
```bash
ollama pull mistral
```

---

## 📁 Project Structure

```
cv_generator/
├── main.py              # Complete application
├── info.txt             # Your personal CV info (not pushed to git)
├── chat_history.json    # Auto-generated chat history
├── requirements.txt     # Dependencies
└── README.md
```

---

## ⚙️ Requirements

```
ollama
fpdf2
```

Install:
```bash
pip install ollama fpdf2
```

---

## 👩‍💻 Built By

**Asma Anika Shahabuddin** — Full Stack Developer & CS Student, Dhaka, Bangladesh

- 🌐 Fiverr: [CodeWithAnika](https://fiverr.com)
- 💼 Upwork: [CodeWithAnika](https://upwork.com)
- 🐙 GitHub: [github.com/anika92](https://github.com/anika92)

---

## 📄 License

MIT License — feel free to use and modify!