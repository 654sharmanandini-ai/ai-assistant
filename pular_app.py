import gradio as gr
from groq import Groq
import edge_tts
import asyncio
import tempfile
import sqlite3
import whisper

# ── DATABASE ──
def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT "New Chat",
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )''')
    conn.commit()
    conn.close()

def create_new_chat():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO chats (title) VALUES ('New Chat')")
    chat_id = c.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def save_message(chat_id, role, content):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
              (chat_id, role, content))
    conn.commit()
    conn.close()

def update_chat_title(chat_id, title):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("UPDATE chats SET title=? WHERE id=?", (title, chat_id))
    conn.commit()
    conn.close()

def get_all_chats():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT id, title FROM chats ORDER BY created_at DESC")
    chats = c.fetchall()
    conn.close()
    return chats

def get_chat_messages(chat_id):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY timestamp", (chat_id,))
    msgs = c.fetchall()
    conn.close()
    history = []
    for msg in msgs:
        history.append({"role": msg[0], "content": msg[1]})
    return history

def get_message_count(chat_id):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE chat_id=?", (chat_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

init_db()

import os
from dotenv import load_dotenv

load_dotenv()
api_key_str = os.environ.get("GROQ_API_KEY", "your_api_key_here")

client = Groq(api_key=api_key_str)

async def text_to_speech(text):
    communicate = edge_tts.Communicate(text, voice="fr-FR-DeniseNeural")
    audio_file = tempfile.mktemp(suffix=".mp3")
    await communicate.save(audio_file)
    return audio_file

def generate_title(first_message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Generate a very short title (3-5 words max) for a chat. Return ONLY the title, no quotes, nothing else."},
            {"role": "user", "content": first_message}
        ],
        max_tokens=15
    )
    return response.choices[0].message.content.strip()

def voice_to_text(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

def get_choices():
    chats = get_all_chats()
    # Sirf title dikhao — ID andar chhupa ke rakhenge
    return [(c[1], str(c[0])) for c in chats]

# ── MAIN FUNCTION ──
def pular_assistant(question, audio_input, chat_history, current_chat_id):
    if audio_input is not None and question.strip() == "":
        question = voice_to_text(audio_input)
        if not question:
            return chat_history, None, "", current_chat_id, gr.update()

    if question.strip() == "":
        return chat_history, None, "", current_chat_id, gr.update()

    if current_chat_id is None:
        current_chat_id = create_new_chat()

    messages = [{"role": "system", "content": """You are a friendly Pular speaking AI assistant named 'Jamma'.
Rules:
- ALWAYS respond naturally in Pular/Fulfulde
- NEVER just translate — give natural conversational response
- Be warm, friendly and engaging
- Keep responses short — 1-2 sentences max"""}]

    for item in chat_history:
        if isinstance(item, dict):
            messages.append({"role": item["role"], "content": item["content"]})

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    response_text = response.choices[0].message.content
    audio_file = asyncio.run(text_to_speech(response_text))

    save_message(current_chat_id, "user", question)
    save_message(current_chat_id, "assistant", response_text)

    if get_message_count(current_chat_id) == 2:
        title = generate_title(question)
        update_chat_title(current_chat_id, title)

    chat_history = chat_history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": response_text}
    ]

    choices = get_choices()
    current_label = str(current_chat_id)
    return chat_history, audio_file, "", current_chat_id, gr.update(choices=choices, value=current_label)

def new_chat_fn():
    chat_id = create_new_chat()
    choices = get_choices()
    current_label = str(chat_id)
    return [], None, "", chat_id, gr.update(choices=choices, value=current_label)

def load_chat_fn(selected, current_chat_id):
    if not selected:
        return [], None, current_chat_id
    try:
        chat_id = int(selected)
        history = get_chat_messages(chat_id)
        return history, None, chat_id
    except:
        return [], None, current_chat_id

# ── UI ──
existing_choices = get_choices()

with gr.Blocks(title="Pular AI", theme=gr.themes.Base(
    primary_hue="purple",
    neutral_hue="slate",
)) as demo:
    current_chat_id = gr.State(None)

    with gr.Row():
        # LEFT SIDEBAR
        with gr.Column(scale=1, min_width=220):
            gr.Markdown("## 🌍 Pular AI")
            new_chat_btn = gr.Button("＋ New Chat", variant="primary", size="lg")
            gr.Markdown("**Recent Chats**")
            chat_list = gr.Dropdown(
                choices=existing_choices,
                label="Select a chat",
                interactive=True
            )

        # MAIN CHAT
        with gr.Column(scale=4):
            gr.Markdown("# Jamma — Pular AI Assistant")
            chatbot = gr.Chatbot(height=420, show_label=False)

            with gr.Row():
                txt = gr.Textbox(
                    placeholder="Message Jamma...",
                    label="Type here",
                    scale=5,
                    lines=1
                )
                submit_btn = gr.Button("Send ➤", variant="primary", scale=1)

            with gr.Row():
                audio_in = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 Voice Input",
                    scale=2
                )
                audio_out = gr.Audio(
                    autoplay=True,
                    label="🔈 AI Response",
                    scale=3
                )

            status = gr.Textbox(label="Status", lines=1, visible=False)

    # EVENTS
    submit_btn.click(
        pular_assistant,
        inputs=[txt, audio_in, chatbot, current_chat_id],
        outputs=[chatbot, audio_out, txt, current_chat_id, chat_list]
    )
    txt.submit(
        pular_assistant,
        inputs=[txt, audio_in, chatbot, current_chat_id],
        outputs=[chatbot, audio_out, txt, current_chat_id, chat_list]
    )
    new_chat_btn.click(
        new_chat_fn,
        outputs=[chatbot, audio_out, txt, current_chat_id, chat_list]
    )
    chat_list.change(
        load_chat_fn,
        inputs=[chat_list, current_chat_id],
        outputs=[chatbot, audio_out, current_chat_id]
    )

demo.launch()