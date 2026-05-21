# Manual Offline Voice Installation

SimpleAudioBookGen no longer downloads or removes voice models. Install offline
voices manually by placing the model files in the folders below.

## Kokoro

Folder:

```text
%APPDATA%\AudioBookGen\models\kokoro
```

Required files:

```text
kokoro-v1.0.onnx
voices-v1.0.bin
```

The app will enable Kokoro voices when both files exist and the optional Python
packages `kokoro-onnx` and `soundfile` are installed.

## Piper

Folder:

```text
%APPDATA%\AudioBookGen\models\piper
```

Required files for each voice:

```text
<voice-id>.onnx
<voice-id>.onnx.json
```

Example for the Spanish voice listed in the app:

```text
es_ES-carlfm-medium.onnx
es_ES-carlfm-medium.onnx.json
```

The app will use Piper voices when the matching files exist and the optional
Python package `piper-tts` is installed.
