import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import torch
from silero_vad import get_speech_timestamps, load_silero_vad

print("[STT] Loading Whisper...")
model = whisper.load_model("tiny")
vad_model = load_silero_vad()
SAMPLERATE = 16000

def listen():
    print("[STT] Listening...")
    
    duration = 5
    try:
        audio = sd.rec(
            int(duration * SAMPLERATE),
            samplerate=SAMPLERATE,
            channels=1,
            dtype="float32"
        )
        sd.wait()
    except Exception as e:
        print(f"[STT] Error recording: {e}")
        return ""

    audio = audio.flatten()

    speech = get_speech_timestamps(
        torch.from_numpy(audio),
        vad_model,
        sampling_rate=SAMPLERATE
    )

    if len(speech) == 0:
        return ""

    start = speech[0]["start"]
    end = speech[-1]["end"]

    speech_audio = audio[int(start):int(end)]

    if len(speech_audio) < 1600:
        return ""

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write(temp_file.name, SAMPLERATE, speech_audio.astype(np.float32))

    result = model.transcribe(
        temp_file.name,
        language="en",
        fp16=False
    )

    return result["text"].strip()
