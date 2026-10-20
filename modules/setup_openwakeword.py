"""Compatibility entry point for the project-local wake-word resource repair."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules.setup_speech import setup_wakeword, WAKE_DIR
from modules.wakeword import WakeWordDetector

if __name__ == "__main__":
    setup_wakeword()
    WakeWordDetector()  # Validate all ONNX sessions without opening a microphone.
    print(f"Wake-word resources validated in {WAKE_DIR}")
