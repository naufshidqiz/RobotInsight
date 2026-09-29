import cv2
import ollama
from PIL import Image
import tempfile
import os
import time

def capture_image():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        return None
    return frame

def capture_and_analyze(question):
    print("[VISION] Capturing image...")
    frame = capture_image()
    if frame is None:
        return "I cannot access the camera."

    # Convert to PIL and show on interface overlay
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    try:
        from modules.interface import show_capture, clear_capture
        show_capture(pil_image)
    except Exception:
        pass  # interface not running, skip overlay

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp_path = tmp.name
    tmp.close()

    cv2.imwrite(tmp_path, frame)

    try:
        response = ollama.chat(
            model="moondream",
            messages=[{
                "role": "user",
                "content": question,
                "images": [tmp_path]
            }]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"[VISION] Error: {e}")
        return "I could not analyze the image."
    finally:
        for _ in range(5):
            try:
                os.remove(tmp_path)
                break
            except PermissionError:
                time.sleep(0.2)
        # Clear the overlay once analysis is done
        try:
            from modules.interface import clear_capture
            clear_capture()
        except Exception:
            pass