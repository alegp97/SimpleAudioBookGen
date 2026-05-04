"""
Motor de síntesis de voz (TTS).

Abstracción con implementaciones:
- EdgeTTSEngine: voces neuronales de Microsoft (principal)
- SAPIEngine: fallback local con pyttsx3/SAPI5
"""

from __future__ import annotations

import asyncio
import os
import time
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from audiobook_gen.config import TTSConfig
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.utils.logger import get_logger

log = get_logger("tts_engine")


class TTSEngine(ABC):
    """Interfaz abstracta para motores TTS."""

    @abstractmethod
    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        """
        Sintetiza un chunk de texto a audio.

        Args:
            chunk: Fragmento de texto a sintetizar.
            output_path: Ruta donde guardar el archivo de audio generado.

        Returns:
            Ruta al archivo de audio generado.
        """
        ...

    @abstractmethod
    def get_voice_name(self) -> str:
        """Retorna el nombre de la voz actual."""
        ...

    @abstractmethod
    def list_voices(self) -> list[str]:
        """Lista las voces disponibles."""
        ...


class EdgeTTSEngine(TTSEngine):
    """
    Motor TTS usando Microsoft Edge Neural Voices.

    Ventajas:
    - Voces neuronales de alta calidad
    - Excelente soporte para español
    - Sin necesidad de GPU
    - Gratuito, sin API key
    - Control de rate, pitch y volumen via SSML
    """

    # Voces recomendadas para español
    RECOMMENDED_VOICES = {
        "es-ES-AlvaroNeural": "España - Hombre (Álvaro)",
        "es-ES-ElviraNeural": "España - Mujer (Elvira)",
        "es-MX-JorgeNeural": "México - Hombre (Jorge)",
        "es-MX-DaliaNeural": "México - Mujer (Dalia)",
        "es-AR-TomasNeural": "Argentina - Hombre (Tomás)",
        "es-CO-GonzaloNeural": "Colombia - Hombre (Gonzalo)",
    }

    def __init__(self, config: Optional[TTSConfig] = None) -> None:
        self.config = config or TTSConfig()
        self._voice = self.config.voice
        self._rate = self.config.rate
        self._pitch = self.config.pitch
        self._volume = self.config.volume

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        """Sintetiza texto usando Edge-TTS con reintentos."""
        import edge_tts
        from pydub import AudioSegment
        import aiohttp

        text = chunk.text.strip()
        if not text:
            log.warning("Chunk %d vacío, generando silencio", chunk.index)
            silence = AudioSegment.silent(duration=500)
            silence.export(output_path, format="mp3")
            return output_path

        async def _generate() -> None:
            communicate = edge_tts.Communicate(
                text,
                voice=self._voice,
                rate=self._rate,
                pitch=self._pitch,
                volume=self._volume,
            )
            await communicate.save(output_path)

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                # Ejecutar síntesis asíncrona
                try:
                    # En Python 3.10+, get_event_loop() puede fallar en hilos secundarios
                    asyncio.run(_generate())
                except RuntimeError as re:
                    # Si ya hay un loop corriendo en este hilo (poco común en worker thread)
                    if "running" in str(re):
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            future = pool.submit(asyncio.run, _generate())
                            future.result(timeout=120)
                    else:
                        raise
                
                # Verificar que el archivo se generó y no está vacío
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    raise RuntimeError(f"El motor TTS no generó audio (archivo vacío o inexistente: {output_path})")

                # Si llegamos aquí, éxito
                log.debug(
                    "Chunk %d sintetizado — %d chars (%d bytes) → %s",
                    chunk.index, len(text), os.path.getsize(output_path), output_path,
                )
                return output_path

            except Exception as e:
                last_error = e
                error_msg = str(e)
                if "503" in error_msg or "Handshake" in error_msg:
                    log.warning(
                        "Error de servidor Edge-TTS (intento %d/%d): %s. Reintentando...",
                        attempt + 1, max_retries, error_msg
                    )
                    time.sleep(2 * (attempt + 1)) # Espera exponencial simple
                else:
                    # Otros errores (ej. timeout)
                    log.error("Error en síntesis (intento %d/%d): %s", attempt + 1, max_retries, e)
                    if attempt == max_retries - 1:
                        raise

        # Si agotamos reintentos
        log.error("Fallo definitivo en Edge-TTS tras %d intentos.", max_retries)
        raise last_error

    def get_voice_name(self) -> str:
        desc = self.RECOMMENDED_VOICES.get(self._voice, self._voice)
        return f"{self._voice} ({desc})"

    def list_voices(self) -> list[str]:
        return list(self.RECOMMENDED_VOICES.keys())


class SAPIEngine(TTSEngine):
    """
    Motor TTS de fallback usando pyttsx3 (SAPI5 en Windows).

    Ventajas:
    - 100% offline
    - Sin dependencias externas

    Limitaciones:
    - Calidad inferior a voces neuronales
    - Prosodia limitada
    """

    def __init__(self, config: Optional[TTSConfig] = None) -> None:
        self.config = config or TTSConfig()
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            import pyttsx3
            self._engine = pyttsx3.init()
            # Configurar rate
            rate = self._engine.getProperty("rate")
            self._engine.setProperty("rate", rate - 25)  # Ligeramente más lento
            # Intentar seleccionar voz en español
            voices = self._engine.getProperty("voices")
            for voice in voices:
                if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                    self._engine.setProperty("voice", voice.id)
                    break
        return self._engine

    def synthesize(self, chunk: TextChunk, output_path: str) -> str:
        """Sintetiza texto usando SAPI5."""
        from pydub import AudioSegment

        text = chunk.text.strip()
        if not text:
            silence = AudioSegment.silent(duration=500)
            silence.export(output_path, format="wav")
            return output_path

        engine = self._get_engine()

        # pyttsx3 guarda en WAV
        wav_path = output_path.replace(".mp3", ".wav")
        engine.save_to_file(text, wav_path)
        engine.runAndWait()

        # Verificar que el archivo WAV se generó (a veces SAPI5 falla silenciosamente)
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
            log.error("SAPI5 no generó el archivo de audio: %s", wav_path)
            raise RuntimeError("El motor SAPI5 falló al generar el archivo de audio.")

        # Convertir a MP3 si es necesario
        if output_path.endswith(".mp3"):
            audio = AudioSegment.from_wav(wav_path)
            audio.export(output_path, format="mp3")
            os.remove(wav_path)

        log.debug("Chunk %d sintetizado (SAPI) — %d chars (%d bytes)", 
                  chunk.index, len(text), os.path.getsize(output_path))
        return output_path

    def get_voice_name(self) -> str:
        return "SAPI5 (Windows)"

    def list_voices(self) -> list[str]:
        try:
            engine = self._get_engine()
            voices = engine.getProperty("voices")
            return [v.name for v in voices]
        except Exception:
            return ["default"]


def create_tts_engine(config: Optional[TTSConfig] = None) -> TTSEngine:
    """
    Factory: crea el motor TTS según la configuración.

    Intenta el motor preferido, con fallback automático.
    """
    config = config or TTSConfig()

    if config.engine == "edge":
        try:
            import edge_tts  # noqa: F401
            log.info("Motor TTS: Edge-TTS (voces neuronales Microsoft)")
            return EdgeTTSEngine(config)
        except ImportError:
            log.warning("edge-tts no instalado. Cayendo a SAPI5...")
            return SAPIEngine(config)

    elif config.engine == "sapi":
        log.info("Motor TTS: SAPI5 (offline)")
        return SAPIEngine(config)

    else:
        log.warning("Motor '%s' no reconocido. Usando Edge-TTS.", config.engine)
        return EdgeTTSEngine(config)
