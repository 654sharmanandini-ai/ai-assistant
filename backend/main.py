from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from groq import Groq
import psycopg2
import psycopg2.extras
import os
import tempfile
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import chromadb
from chromadb.utils import embedding_functions
import imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
print(f"FFmpeg path: {ffmpeg_path}")

app = FastAPI()

# RAG Setup
try:
    chroma_client = chromadb.PersistentClient(path="./pular_db")
    ef = embedding_functions.DefaultEmbeddingFunction()
    pular_collection = chroma_client.get_collection(
        name="pular_knowledge",
        embedding_function=ef
    )
    print(f"RAG loaded: {pular_collection.count()} Pular entries")
    RAG_ENABLED = True
except Exception as e:
    print(f"RAG not available: {e}")
    RAG_ENABLED = False

def get_pular_context(user_message: str) -> str:
    if not RAG_ENABLED:
        return ""
    try:
        results = pular_collection.query(
            query_texts=[user_message],
            n_results=5
        )
        lines = []
        for doc in results["documents"][0]:
            lines.append(f"  - {doc}")
        return "\n".join(lines)
    except:
        return ""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── CONFIG ──
SECRET_KEY = "pular-ai-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
DB_URL = "postgresql://postgres:root123@localhost/pular_ai"
GROQ_API_KEY = "apni_groq_key_yahan"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
api_key_str = os.environ.get("GROQ_API_KEY", "your_api_key_here")

client = Groq(api_key=api_key_str)

# ── DB CONNECTION ──
def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn

# ── AUTH HELPERS ──
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_optional_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login", auto_error=False))):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return user_id
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── DB HELPERS ──
def save_message(chat_id, role, content):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, role, content) VALUES (%s, %s, %s)", (chat_id, role, content))
    conn.commit()
    conn.close()

def get_chat_messages(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE chat_id=%s ORDER BY timestamp", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

def get_message_count(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE chat_id=%s", (chat_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def update_title(chat_id, title):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE chats SET title=%s WHERE id=%s", (title, chat_id))
    conn.commit()
    conn.close()

# ── AUTH ROUTES ──
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(req: RegisterRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email=%s", (req.email,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(req.password)
    c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (req.name, req.email, hashed))
    user_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    token = create_token({"user_id": user_id})
    return {"token": token, "name": req.name, "email": req.email}

@app.post("/login")
def login(req: LoginRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, password FROM users WHERE email=%s", (req.email,))
    user = c.fetchone()
    conn.close()
    if not user or not verify_password(req.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"user_id": user[0]})
    return {"token": token, "name": user[1], "email": req.email}

@app.get("/me")
def get_me(user_id: int = Depends(get_optional_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, email FROM users WHERE id=%s", (user_id,))
    user = c.fetchone()
    conn.close()
    return {"name": user[0], "email": user[1]}

# ── CHAT ROUTES ──
@app.get("/chats")
def get_chats(user_id: int = Depends(get_optional_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title FROM chats WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1]} for r in rows]

@app.post("/chats")
def create_chat(user_id: int = Depends(get_optional_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO chats (user_id, title) VALUES (%s, 'New Chat') RETURNING id", (user_id if user_id else None,))
    chat_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": chat_id, "title": "New Chat"}

@app.get("/chats/{chat_id}/messages")
def get_messages(chat_id: int, user_id: int = Depends(get_optional_user)):
    return get_chat_messages(chat_id)

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, user_id: int = Depends(get_optional_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE chat_id=%s", (chat_id,))
    c.execute("DELETE FROM chats WHERE id=%s", (chat_id,))
    conn.commit()
    conn.close()
    return {"success": True}

class RenameRequest(BaseModel):
    title: str

@app.put("/chats/{chat_id}/rename")
def rename_chat(chat_id: int, req: RenameRequest, user_id: int = Depends(get_optional_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE chats SET title=%s WHERE id=%s", (req.title, chat_id))
    conn.commit()
    conn.close()
    return {"success": True}

class MessageRequest(BaseModel):
    chat_id: int
    message: str
    history: list

@app.post("/chat")
async def chat(req: MessageRequest, user_id: int = Depends(get_optional_user)):
    pular_context = get_pular_context(req.message)
    messages = [
        {
            "role": "system",
            "content": f"""You are 'Jamma', a friendly AI assistant who ONLY speaks Pular/Fulfulde language of Fuuta Jallon, Guinea.
             You are like ChatGPT but in Pular language only.

             RULES:
             - ALWAYS respond in Pular/Fulfulde ONLY
             - Never use English or French
             - Be friendly, warm, conversational
             - Give natural responses like a real conversation
             - You are an AI assistant — no family, no personal life
             - If asked who you are: "Mi ko Jamma, ceedoowo maa e Pular!"

             EXAMPLES:
             User: "hello" → "A jaraama! No wa'i?"
             User: "how are you" → "Jam tun! Hiða e jam?"
             User: "tell me something" → "Miðo selli! En haala e Pular!"
             User: "goodbye" → "En jango! Waalen e jam!"

             RELEVANT PULAR PHRASES:
             {pular_context}

             Respond naturally in Pular like a friendly native speaker."""   
        }
    ]
    for msg in req.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": req.message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    response_text = response.choices[0].message.content

    save_message(req.chat_id, "user", req.message)
    save_message(req.chat_id, "assistant", response_text)

    title = None
    if get_message_count(req.chat_id) == 2:
        title_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a chat title generator. Create a specific, meaningful title (3-5 words) that accurately describes what this conversation is about. Base it on the actual content of the user's message and AI reply. Return ONLY the title."""
                },
                {
                    "role": "user",
                   "content": f"The user said: '{req.message}'. Generate a title based only on what the USER said, ignore the AI reply. Return ONLY the title."
                }
            ],
            max_tokens=20
        )
        title = title_response.choices[0].message.content.strip()
        update_title(req.chat_id, title)

    return {"response": response_text, "title": title}

@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    import whisper
    import subprocess
    import numpy as np
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    converted_path = tmp_path + "_converted.wav"
    
    subprocess.run([
        ffmpeg_exe, "-i", tmp_path,
        "-ar", "16000", "-ac", "1",
        "-y", converted_path
    ], capture_output=True)
    
    result_proc = subprocess.run([
        ffmpeg_exe, "-i", converted_path,
        "-f", "s16le", "-ar", "16000",
        "-ac", "1", "-"
    ], capture_output=True)
    
    audio = np.frombuffer(result_proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    
    model = whisper.load_model("base")
    result = model.transcribe(audio, fp16=False)
    
    os.unlink(tmp_path)
    try:
        os.unlink(converted_path)
    except:
        pass
    
    return {"text": result["text"]}

@app.post("/tts")
async def tts(req: dict):
    import edge_tts
    text = req.get("text", "")
    communicate = edge_tts.Communicate(text, voice="fr-FR-DeniseNeural")
    tmp = tempfile.mktemp(suffix=".mp3")
    await communicate.save(tmp)
    from fastapi.responses import FileResponse
    return FileResponse(tmp, media_type="audio/mpeg")