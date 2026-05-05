"""
Voice Synthesis Engine (TTS).
Abstractions with implementations:
- EdgeTTSEngine:  Microsoft Neural Voices (online, primary)
- KokoroEngine:   Lightweight ONNX model (offline)
- PiperEngine:    Ultra-fast synthesis (offline)
- SAPIEngine:     Local fallback using pyttsx3/SAPI5 (Windows)
"""

from __future__ import annotations

import asyncio
import os
import time
import tempfile
import wave
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from audiobook_gen.config import TTSConfig
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.utils.logger import get_logger

log = get_logger("tts_engine")

class TTSEngine(ABC):
    @abstractmethod
    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        pass

class EdgeTTSEngine(TTSEngine):
    def __init__(self, config: TTSConfig, voice_id: str):
        self.config = config
        self.voice_id = voice_id

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        import edge_tts
        async def _run():
            communicate = edge_tts.Communicate(chunk.text, self.voice_id)
            await communicate.save(output_path)
        asyncio.run(_run())
        return output_path

class KokoroEngine(TTSEngine):
    def __init__(self, config: TTSConfig, voice_id: str):
        import kokoro_onnx
        from audiobook_gen.voices import kokoro_model_dir
        model_path = kokoro_model_dir() / "kokoro-v1.0.onnx"
        voices_path = kokoro_model_dir() / "voices-v1.0.bin"
        self.kokoro = kokoro_onnx.KokoroONNX(str(model_path), str(voices_path))
        self.voice_id = voice_id

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        import soundfile as sf
        samples, rate = self.kokoro.create(chunk.text, voice=self.voice_id, speed=1.0)
        sf.write(output_path, samples, rate)
        return output_path

class PiperEngine(TTSEngine):
    def __init__(self, config: TTSConfig, voice_id: str):
        from piper import PiperVoice
        from audiobook_gen.voices import piper_model_dir
        model_path = piper_model_dir() / f"{voice_id}.onnx"
        self.voice = PiperVoice.load(str(model_path))

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.voice.config.sample_rate)
            self.voice.synthesize(chunk.text, wav_file)
        return output_path

class SAPIEngine(TTSEngine):
    def __init__(self, config: TTSConfig, voice_id: str):
        import pyttsx3
        self.engine = pyttsx3.init()
        if voice_id and voice_id != "System Default":
            self.engine.setProperty('voice', voice_id)

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        self.engine.save_to_file(chunk.text, output_path)
        self.engine.runAndWait()
        return output_path

def create_tts_engine(config: TTSConfig, voice_id: str) -> TTSEngine:
    engine_type = config.engine.lower()
    if "edge" in engine_type:
        return EdgeTTSEngine(config, voice_id)
    elif "kokoro" in engine_type:
        return KokoroEngine(config, voice_id)
    elif "piper" in engine_type:
        return PiperEngine(config, voice_id)
    else:
        return SAPIEngine(config, voice_id)
