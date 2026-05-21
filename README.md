# SimpleAudioBookGen — PDF to Audiobook

[![Release](https://img.shields.io/badge/release-0.1.0--beta-blue.svg)](https://github.com/alegp97/SimpleAudioBookGen/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

**Turn PDFs into MP3 audiobooks in a few clicks.**

SimpleAudioBookGen is a lightweight Windows desktop tool designed to convert PDF documents into high-quality MP3 audiobooks. No complex libraries, no heavy platforms—just a simple, guided workflow to get your audiobooks ready for any device.

---

## ✨ Features

- **PDF to MP3:** High-fidelity conversion of documents to audio.
- **Natural AI Voices:** Powered by advanced neural text-to-speech for human-like reading.
- **Offline Modes:** Support for local synthesis using Kokoro, Piper, and SAPI5.
- **OCR Support:** Extract text from scanned or image-based PDFs using Tesseract.
- **Smart Cleaning:** Automatic removal of headers, footers, and page numbers.
- **Voice Preview:** Test voices and languages before starting the conversion.
- **Progress Tracking:** Real-time feedback and estimation of duration.

---

## 🎙️ Voice Modes

1.  **Natural Online Voice (Recommended):** Best quality, uses Microsoft Edge TTS neural voices. Requires internet.
2.  **Offline Neural Voice:** High-quality local synthesis using the Kokoro ONNX model.
3.  **Fast Offline Voice:** Ultra-fast local synthesis using Piper.
4.  **Basic System Voice:** Uses Windows SAPI5 (legacy) for 100% offline fallback.

---

## 🚀 Getting Started

### Installation (Pre-built)
1. Download the latest installer from the [Releases](https://github.com/alegp97/SimpleAudioBookGen/releases) page.
2. Run `SimpleAudioBookGen-Setup.exe`.
3. Launch from your Start Menu.

### Development Setup
If you want to run from source or contribute:

```bash
# Clone the repository
git clone https://github.com/alegp97/SimpleAudioBookGen.git
cd SimpleAudioBookGen

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m audiobook_gen
```

---

## 🛠️ Build from Source
To generate a standalone executable and installer:

1.  **Prepare FFmpeg:** Place `ffmpeg.exe` and `ffprobe.exe` in the `.ffmpeg_bin` folder (or let `build.py` download them).
2.  **Build EXE:**
    ```bash
    python build.py
    ```
3.  **Generate Installer:** Use Inno Setup with the provided `installer.iss` file.

---

## 🔒 Privacy
SimpleAudioBookGen respects your privacy.
- **Local First:** Most processing happens on your machine.
- **Online Mode:** Only the "Natural Online" mode sends text to Microsoft services for synthesis.
- **No Analytics:** We do not track your usage or collect your documents.
Read our full [Privacy Policy](docs/PRIVACY_POLICY.md) for more details.

---

## 🤝 Support
Encountered a bug? Need help?
- Check the [Support Guide](docs/SUPPORT.md).
- Open an issue on [GitHub Issues](https://github.com/alegp97/SimpleAudioBookGen/issues).

---

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details (coming soon).
Built with PySide6, PyMuPDF, and Edge-TTS.
