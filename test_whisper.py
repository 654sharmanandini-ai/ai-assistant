import whisper

print("Loading Whisper model...")
model = whisper.load_model("base")

print("Transcribing Pular audio...")
result = model.transcribe("test_pular.mp3", language="fr")

print("\n--- Result ---")
print("Text:", result["text"])
print("Language:", result["language"])
print("\n✅ Whisper test complete!")