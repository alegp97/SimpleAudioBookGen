# SimpleAudioBookGen Stabilization Notes

The stable route for this phase is Edge-TTS, with SAPI5 as a basic local
Windows fallback. Kokoro and Piper remain optional offline engines: users place
their model files manually in the documented folders. If those dependencies or
models are missing, the application should show a clear actionable error.

The build should not package fake binaries. FFmpeg and Tesseract must be real
executables before they are included in the Windows distribution.
