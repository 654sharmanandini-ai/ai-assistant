# Pular Voice AI Assistant

A full-stack Voice-to-Voice AI Assistant designed for the Pular/Fulfulde language. This project leverages natural language processing and voice synthesis to provide real-time conversational capabilities.

## Features

* Voice-to-Text (ASR) using OpenAI Whisper
* Text-to-Speech (TTS) using Edge-TTS
* Large Language Model integration via Groq API (Llama 3)
* Retrieval-Augmented Generation (RAG) using ChromaDB
* Dual database architecture: PostgreSQL for authentication, SQLite for chat history
* REST API backend built with FastAPI
* Interactive web interfaces using React.js and Gradio

## Technology Stack

* **Backend**: Python, FastAPI, Uvicorn
* **Frontend**: React.js, Gradio
* **Databases**: PostgreSQL, SQLite, ChromaDB
* **Machine Learning**: Whisper, Edge-TTS, Llama-3

## Installation and Setup

### 1. Prerequisites

* Python 3.10 or higher
* Node.js and npm
* FFmpeg

### 2. Clone the Repository

```bash
git clone https://github.com/654sharmanandini-ai/ai-assistant.git
cd ai-assistant
```

### 3. Environment Variables

Create a `.env` file in the root directory and add your API keys:

```text
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Backend Setup

```bash
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn groq whisper edge-tts gradio psycopg2 chromadb bcrypt python-jose python-dotenv
```

### 5. Running the Application

**Gradio Interface:**

```bash
python pular_app.py
```

**Full-Stack Application:**

Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

Start the frontend server:
```bash
cd frontend
npm install
npm start
```

## Security

Ensure that your `.env` file is never committed to version control. It is included in `.gitignore` by default.

## License

MIT License
