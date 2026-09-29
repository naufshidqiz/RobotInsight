import numpy as np
import sounddevice as sd
from openwakeword.model import Model
import os
import time

class WakeWordDetector:
    def __init__(self):
        print("[WAKEWORD] Initializing...")
        module_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(module_dir, "hey_in_site.onnx")

        print(f"[WAKEWORD] Looking for model at: {model_path}")
        print(f"[WAKEWORD] Model exists: {os.path.exists(model_path)}")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Custom wake word model not found: {model_path}")

        try:
            self.owwModel = Model(
                wakeword_models=[model_path],
                inference_framework="onnx"
            )
            self.samplerate = 16000
            self.chunk_size = 1280
            print("[WAKEWORD] Custom model 'hey_in_site.onnx' loaded successfully!")
        except Exception as e:
            print(f"[WAKEWORD] Error loading model: {e}")
            raise

    def start_listening(self):
        print("[WAKEWORD] Listening for 'Hey In Site'...")

        # Reset model scores so leftover high scores don't instantly re-trigger
        self.owwModel.reset()

        # How many chunks must score HIGH in a row before we accept it
        # Prevents a single noisy frame from triggering
        THRESHOLD = 0.7          # raised from 0.5 — less sensitive to background noise
        CONFIRM_CHUNKS = 2       # must exceed threshold 2 times in a row
        COOLDOWN_AFTER = 1.5     # seconds to ignore after "Going to sleep" speak finishes

        time.sleep(COOLDOWN_AFTER)  # drain any residual audio from previous session

        consecutive = 0

        with sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.chunk_size,
            dtype="int16"
        ) as stream:
            while True:
                audio, _ = stream.read(self.chunk_size)
                if len(audio) == 0:
                    continue

                predictions = self.owwModel.predict(audio.flatten())

                detected = any(score > THRESHOLD for score in predictions.values())

                if detected:
                    consecutive += 1
                    if consecutive >= CONFIRM_CHUNKS:
                        score = max(predictions.values())
                        print(f"[WAKEWORD] Confirmed wake word (Score: {score:.2f})")
                        self.owwModel.reset()  # clear state so it doesn't re-fire
                        return
                else:
                    consecutive = 0  # reset streak if any chunk drops below threshold
