from groq import Groq
from gtts import gTTS
import os

# Groq client
try:
    with open("keys.txt", "r") as f:
        api_key_str = f.read().strip()
except Exception:
    api_key_str = "your_api_key_here"

client = Groq(api_key=api_key_str)

print("Pular AI Assistant - Text Test")
print("=" * 40)

# Question English mein
question = "How do you say hello and good morning in Pular language?"

print(f"Question: {question}")
print("\nThinking...")

# Groq LLM se Pular response lo
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a Pular/Fulfulde language expert. When asked questions, always respond with Pular/Fulfulde translations and explanations."
        },
        {
            "role": "user",
            "content": question
        }
    ]
)

response_text = response.choices[0].message.content
print(f"\n[OK] AI Response:\n{response_text}")

# Audio bhi banao
tts = gTTS(text=response_text, lang='fr')
tts.save("pular_response.mp3")
print("\n[Audio] Audio saved: pular_response.mp3")