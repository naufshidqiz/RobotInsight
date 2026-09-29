# RobotInsight

RobotInsight is a Windows voice-controlled assistant with a wake word, speech recognition, a local Ollama language model, web search, camera description, and spoken replies. Its models run locally; web-search questions need an internet connection.

## What your PC needs

**Required**

- Windows 10 or 11, 64-bit
- Git for Windows
- Python 3.11, 64-bit, with the Python Launcher and Tcl/Tk selected during installation
- Ollama for Windows
- A microphone and speakers or headphones
- Internet access for the first setup, model downloads, and web search
- At least 15 GB of free disk space for Python packages and the local models

**Recommended**

- 16 GB RAM for smoother use; 8 GB may work but can be slow or run out of memory
- A recent 4-core-or-better processor
- An NVIDIA GPU can improve local model speed, but is optional
- A webcam for camera questions

The Mistral model alone is about 4.4 GB. RobotInsight also downloads its vision model, speech-recognition assets, and a Piper voice on first setup. The app can run without a webcam, but its vision feature needs one.

## First-time setup

1. Install [Python 3.11 for Windows](https://www.python.org/downloads/release/python-3119/). In the installer, enable the Python Launcher and Tcl/Tk options.
2. Install [Ollama for Windows](https://ollama.com/download/windows). Ollama supplies the local language and vision models.
3. Open PowerShell or Command Prompt and clone this repository:

   ```powershell
   git clone https://github.com/naufshidqiz/RobotInsight.git
   cd RobotInsight
   ```

4. Double-click **Start_RobotInsight.bat**.

The launcher creates a private Python environment, installs the packages, downloads the Piper voice and required Ollama models, and starts the assistant. First setup can take a while and download several gigabytes. Later runs reuse the installed packages and models.

When the robot is ready, say **“Hey In Site”** and then ask a question. Press Escape to leave fullscreen. Close the terminal window or press Ctrl+C there to stop the program.

## Microphone and camera

The app uses the Windows default microphone. If it does not hear you, select the intended input device in **Windows Settings → System → Sound → Input**, then restart the app. Allow microphone and camera access for desktop apps in Windows Privacy settings.

The camera feature opens the first available camera. If your PC has multiple cameras and the wrong one opens, update the camera index in `modules/vision.py` (`cv2.VideoCapture(0)`).

## Features to try

- “What time is it?”
- “What is a transistor?” — searches the web and summarizes results
- “Search for the latest NASA Artemis news.”
- “Can you explain that more simply?” — follows up on the previous answer
- “What do you see?” — describes the webcam image
- “Tell me a short joke.” — general conversation through the local model

More test phrases are in [TEST_PHRASES.md](TEST_PHRASES.md).

## Troubleshooting

- **Python 3.11 was not found:** install the 64-bit Python version linked above, including the Python Launcher, then reopen the `.bat` file.
- **Ollama was not found:** install Ollama and reopen the launcher.
- **Ollama cannot connect:** open Ollama from the Start menu and try again.
- **Microphone errors:** choose a working Windows default input device and check microphone privacy permissions.
- **Dependency setup needs to run again:** delete `.setup_complete` and launch the `.bat` file again.
- **The model is slow:** Ollama can use the CPU, but a faster processor or supported GPU improves response time. The app currently uses the `mistral:latest` model.

## Privacy and network use

Speech recognition, language generation, vision analysis, and text-to-speech run on the PC. The assistant sends web-search queries to its search provider when web lookup is needed. The first run downloads Python packages and model files. No API key is required.
