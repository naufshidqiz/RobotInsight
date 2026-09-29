import os
import glob

# Adjust this to your actual project path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folders are in root

FOLDERS = ["Warmup", "Idle", "Listening", "Thinking", "Speaking", "Capturing"]

print(f"Looking for images in: {BASE_DIR}")
print(f"Folder exists: {os.path.exists(BASE_DIR)}\n")

for folder in FOLDERS:
    path  = os.path.join(BASE_DIR, folder)
    files = sorted(glob.glob(os.path.join(path, "*.jpg")) +
                   glob.glob(os.path.join(path, "*.JPG")) +
                   glob.glob(os.path.join(path, "*.png")))
    exists = os.path.exists(path)
    print(f"  {folder}/  (exists={exists})  →  {len(files)} files")
    for f in files:
        print(f"    {os.path.basename(f)}")