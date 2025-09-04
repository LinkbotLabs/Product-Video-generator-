from gtts import gTTS

def generate_tts(text, output_path="audio.mp3", lang="en"):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    print(f"🎙️ Audio saved to: {output_path}")
    return output_path
