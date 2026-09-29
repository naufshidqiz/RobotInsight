import subprocess
import tempfile
import sounddevice as sd
import soundfile as sf
import re
import os
import unicodedata
import sys

# Piper model is in the modules folder (same as this file)
VOICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_GB-alan-medium.onnx")

def clean_text(text):
    # Strip hidden reasoning tags and non-spoken punctuation/symbols before Piper.
    text = re.sub(r'<think>.*?(?:</think>|$)', '', text, flags=re.IGNORECASE | re.DOTALL)
    cleaned = []
    for index, char in enumerate(text):
        category = unicodedata.category(char)
        if category.startswith("P") or category.startswith("S"):
            if char in ("'", "’") and index > 0 and index + 1 < len(text) \
                    and text[index - 1].isalpha() and text[index + 1].isalpha():
                cleaned.append("'")
            elif char in ".!?。！？":
                cleaned.append("\n")
            else:
                cleaned.append(" ")
        else:
            cleaned.append(char)
    text = "".join(cleaned)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n+ *", "\n", text)
    return text.strip()

def speak(text):
    if not text:
        return
        
    text = clean_text(text)
    if not text:
        return
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

    try:
        command = [
            sys.executable,
            "-m",
            "piper",
            "--model",
            VOICE_PATH,
            "--output_file",
            output_path
        ]
        
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        process.communicate(text)
        
        if os.path.exists(output_path):
            data, samplerate = sf.read(output_path)
            sd.play(data, samplerate)
            sd.wait()
            os.remove(output_path)
        else:
            print("[TTS] Error: Output file not created. Is Piper installed?")
            
    except Exception as e:
        print(f"[TTS] Error: {e}")
