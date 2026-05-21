# Privacy Policy

**Effective Date:** May 15, 2024

SimpleAudioBookGen ("the App") is a desktop application designed to convert PDF files into MP3 audiobooks. Your privacy is important to us. This policy explains how the App handles your data.

## 1. Data Collection
SimpleAudioBookGen is designed to operate with minimal data collection:
- **No Account Required:** You do not need to create an account to use the App.
- **Local Processing:** By default, the App processes your PDF files locally on your computer.
- **No Personal Data Collection:** The App does not intentionally collect, store, or transmit personal identification information (such as your name, email, or address).

## 2. Audio Generation Modes
The App offers different voice modes that handle data differently:

### A. Natural Online Voice Mode
When you use the "Natural Online" voice mode, the App sends portions of the text extracted from your PDF to a third-party text-to-speech service (Microsoft Edge TTS) to generate the audio.
- **Risk:** Do not use this mode for sensitive or confidential documents if you are not comfortable with text being processed by an online service.
- **Data Handling:** The text is sent only for synthesis and is not stored by SimpleAudioBookGen.

### B. Offline Voice Modes (Kokoro, Piper, SAPI5)
These modes process all text locally on your machine. No text is sent over the internet.

## 3. OCR (Optical Character Recognition)
If you choose to process a scanned PDF, the App may use Tesseract OCR. This process happens entirely on your local machine.

## 4. Logs and Debugging
The App may generate local log files (`audiobook_gen.log`) on your computer for diagnostic purposes.
- These logs may contain technical information about the conversion process.
- They are stored only on your device and are not automatically sent to us.

## 5. Third-Party Services
The App uses the following third-party libraries and services:
- **Microsoft Edge TTS:** Used for high-quality online voices.
- **PyMuPDF:** Used for PDF text extraction.
- **FFmpeg:** Used for audio assembly.

## 6. Changes to This Policy
We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy within the App's repository or documentation.

## 7. Contact Us
If you have questions about this Privacy Policy, please open an issue on our [GitHub repository](https://github.com/alegp97/SimpleAudioBookGen/issues).
