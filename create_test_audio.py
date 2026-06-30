from gtts import gTTS

# Pular text se audio banana
text = "Jam waawi. Tanalde. Mi yidi Pulaar."

tts = gTTS(text=text, lang='fr')
tts.save("test_pular.mp3")

print("✅ test_pular.mp3 created!")