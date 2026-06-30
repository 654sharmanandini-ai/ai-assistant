# Pular Voice AI Assistant 🌍

A full-stack, multilingual Voice-to-Voice AI Assistant designed specifically for the **Pular/Fulfulde** language. Built using cutting-edge AI models, this assistant provides natural, conversational, and ultra-fast voice interactions.

## 🚀 Features

- **Voice-to-Text (ASR)**: High-accuracy speech recognition using OpenAI's **Whisper** model.
- **Ultra-Fast LLM**: Context-aware, intelligent conversations using **Groq API (Llama-3.3-70b)**.
- **Text-to-Speech (TTS)**: Natural voice synthesis using **Edge-TTS**.
- **Context & Knowledge (RAG)**: Retrieval-Augmented Generation powered by **ChromaDB**.
- **Full-Stack Architecture**: Robust **FastAPI** backend, **React** frontend, and a **Gradio** web interface.
- **Database**: Dual database setup using **PostgreSQL** (Authentication) and **SQLite** (Chat History).

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, PostgreSQL, SQLite
- **Frontend**: React.js, Gradio
- **AI/ML**: OpenAI Whisper, Edge-TTS, Groq (Llama-3), ChromaDB

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- FFmpeg (for audio processing)

### 2. Clone the Repository
```bash
git clone https://github.com/654sharmanandini-ai/ai-assistant.git
cd ai-assistant
```

### 3. Setup API Keys
Create a file named `.env` in the root directory and paste your **Groq API Key** inside it:
```text
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Setup Python Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# Install dependencies
pip install fastapi uvicorn groq whisper edge-tts gradio psycopg2 chromadb bcrypt python-jose
```

### 5. Running the Application

**Option A: Run the Gradio App (All-in-one UI)**
```bash
python pular_app.py
```

**Option B: Run the Full-Stack (FastAPI + React)**
1. **Start the Backend:**
```bash
cd backend
uvicorn main:app --reload
```
2. **Start the Frontend:**
Open a new terminal and run:
```bash
cd frontend
npm install
npm start
```

## 🔒 Security Note
Do not commit your `keys.txt` or `.env` files to GitHub. This repository uses `.gitignore` to keep API keys secure.

## 📄 License
This project is open-source and available under the MIT License.
