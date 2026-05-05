"""
Voice catalogue and management.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class VoiceEntry:
    id: str
    display_name: str
    language: str
    locale: str
    gender: str
    engine: str  # 'edge', 'kokoro', 'piper', 'sapi'
    model_url: Optional[str] = None  # For Piper/Kokoro downloads

# Language display names for the combo box
LANGUAGE_ORDER = [
    "English", "Spanish", "French", "German", "Portuguese",
    "Italian", "Japanese", "Chinese", "Russian", "Arabic",
    "Korean", "Hindi"
]

# Sample texts for previews
SAMPLE_TEXTS = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Spanish": "El veloz murciélago hindú comía feliz cardillo y kiwi.",
    "French": "Portez ce vieux vieux vieux vieux vieux vieux vieux.",
    "German": "Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.",
    "Portuguese": "O rápido raposo castanho salta sobre o cão preguiçoso.",
    "Italian": "Qualche vago barlume di speranza.",
    "Japanese": "素早い茶色の狐が、のろまな犬を飛び越えます。",
    "Chinese": "敏捷的棕色狐狸跳过了那只懒狗。",
    "Russian": "Съешь ещё этих мягких французских булок, да выпей чаю.",
    "Arabic": "الثعلب البني السريع يقفز فوق الكلب الكسول.",
    "Korean": "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "Hindi": "तेज़ भूरी लोमड़ी आलसी कुत्ते के ऊपर से कूद गई।"
}

# Edge-TTS Neural Voices
EDGE_VOICES = {
    "English": [
        VoiceEntry("en-US-AndrewNeural", "Andrew (Male)", "English", "en-US", "Male", "edge"),
        VoiceEntry("en-US-AvaNeural", "Ava (Female)", "English", "en-US", "Female", "edge"),
        VoiceEntry("en-GB-SoniaNeural", "Sonia (Female, UK)", "English", "en-GB", "Female", "edge"),
    ],
    "Spanish": [
        VoiceEntry("es-ES-AlvaroNeural", "Alvaro (Male, Spain)", "Spanish", "es-ES", "Male", "edge"),
        VoiceEntry("es-ES-ElviraNeural", "Elvira (Female, Spain)", "Spanish", "es-ES", "Female", "edge"),
        VoiceEntry("es-MX-DaliaNeural", "Dalia (Female, Mexico)", "Spanish", "es-MX", "Female", "edge"),
    ],
    # ... (other languages omitted for brevity in this scratchpad, but I'll include the main ones)
}

# Kokoro v1.0 Voices
KOKORO_VOICES = {
    "English": [
        VoiceEntry("af_heart", "Heart (Female)", "English", "en-US", "Female", "kokoro"),
        VoiceEntry("am_adam", "Adam (Male)", "English", "en-US", "Male", "kokoro"),
    ],
    "Spanish": [
        VoiceEntry("es_alex", "Alex (Male)", "Spanish", "es-ES", "Male", "kokoro"),
        VoiceEntry("es_elena", "Elena (Female)", "Spanish", "es-ES", "Female", "kokoro"),
    ]
}

KOKORO_MODEL_INFO = {
    "url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices_url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
}

# Piper Voices
PIPER_VOICES = {
    "English": [
        VoiceEntry("en_US-libritts-high", "LibriTTS (High Quality)", "English", "en-US", "Male", "piper",
                   "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx"),
        VoiceEntry("en_GB-southern_english_female-low", "Southern (Female, Low)", "English", "en-GB", "Female", "piper",
                   "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/southern_english_female/low/en_GB-southern_english_female-low.onnx"),
    ],
    "Spanish": [
        VoiceEntry("es_ES-carlfm-medium", "Carl (Male, Spain)", "Spanish", "es-ES", "Male", "piper",
                   "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx"),
    ]
}

def kokoro_model_dir() -> Path:
    p = Path(os.environ.get("APPDATA", "")) / "AudioBookGen" / "models" / "kokoro"
    p.mkdir(parents=True, exist_ok=True)
    return p

def piper_model_dir() -> Path:
    p = Path(os.environ.get("APPDATA", "")) / "AudioBookGen" / "models" / "piper"
    p.mkdir(parents=True, exist_ok=True)
    return p

def is_kokoro_installed() -> bool:
    return (kokoro_model_dir() / "kokoro-v1.0.onnx").exists()

def is_piper_voice_installed(voice_id: str) -> bool:
    return (piper_model_dir() / f"{voice_id}.onnx").exists()

def get_installed_piper_voices() -> list[str]:
    return [f.stem for f in piper_model_dir().glob("*.onnx")]
