from openwakeword.utils import download_models
import os

print("Downloading openWakeWord resources...")
try:
    download_models()
    model_dir = os.path.join(os.path.expanduser("~"), ".openwakeword", "models")
    print(f"Done. Models saved to {model_dir}")
    
    # List downloaded models
    if os.path.exists(model_dir):
        models = [f for f in os.listdir(model_dir) if f.endswith(".onnx")]
        print(f"Available models: {models}")
except Exception as e:
    print(f"Error downloading models: {e}")
    print("You may need to download models manually from GitHub")