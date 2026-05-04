"""
Ensamblado y postproceso de audio.

Une fragmentos de audio, inserta silencios entre secciones,
normaliza volumen y exporta a MP3.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

from pydub import AudioSegment

from audiobook_gen.config import AudioConfig
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.utils.logger import get_logger

log = get_logger("audio_assembler")


class AudioAssembler:
    """Ensambla fragmentos de audio en un audiolibro completo."""

    def __init__(self, config: Optional[AudioConfig] = None) -> None:
        self.config = config or AudioConfig()

    def assemble(
        self,
        audio_paths: list[str],
        chunks: list[TextChunk],
        output_path: str,
    ) -> str:
        """
        Ensambla los fragmentos de audio en un MP3 final usando FFmpeg stream copy.
        """
        if not audio_paths:
            raise ValueError("No hay fragmentos de audio para ensamblar")

        log.info("Ensamblando %d fragmentos de audio con FFmpeg...", len(audio_paths))

        temp_dir = os.path.dirname(audio_paths[0])
        silence_para_path = os.path.join(temp_dir, "silence_para.mp3")
        silence_chap_path = os.path.join(temp_dir, "silence_chap.mp3")

        # 1. Ensure silence files exist
        if not os.path.exists(silence_para_path):
            AudioSegment.silent(duration=self.config.silence_paragraph_ms).export(
                silence_para_path, format="mp3", bitrate=self.config.mp3_bitrate
            )
        if not os.path.exists(silence_chap_path):
            AudioSegment.silent(duration=self.config.silence_chapter_ms).export(
                silence_chap_path, format="mp3", bitrate=self.config.mp3_bitrate
            )

        # 2. Build the concat list
        concat_txt_path = os.path.join(temp_dir, "concat.txt")
        
        def _escape_path(p: str) -> str:
            # FFmpeg concat requires escaping single quotes
            return p.replace("'", "'\\''")

        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for i, (audio_path, chunk) in enumerate(zip(audio_paths, chunks)):
                f.write(f"file '{_escape_path(audio_path)}'\n")

                if i < len(audio_paths) - 1:
                    if chunk.is_chapter_end:
                        f.write(f"file '{_escape_path(silence_chap_path)}'\n")
                        log.debug("Pausa de capítulo insertada tras chunk %d", chunk.index)
                    elif self._chunk_ends_sentence(chunk.text):
                        f.write(f"file '{_escape_path(silence_para_path)}'\n")

        # 3. Run FFmpeg concat demuxer with stream copy
        ffmpeg_exe = getattr(AudioSegment, "converter", "ffmpeg")
        cmd = [
            str(ffmpeg_exe),
            "-y",  # Overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt_path,
            "-c", "copy",
            output_path
        ]

        try:
            log.info("Ejecutando FFmpeg stream copy...")
            kwargs = {"check": True, "capture_output": True, "text": True}
            if os.name == 'nt':
                kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            result = subprocess.run(cmd, **kwargs)
            log.debug("FFmpeg output: %s", result.stderr)
        except subprocess.CalledProcessError as e:
            log.error("Error crítico ensamblando audio con FFmpeg: %s", e.stderr)
            raise RuntimeError(f"Fallo al ensamblar audio: {e.stderr}") from e

        # 4. Final metadata logging
        duration_secs = 0.0
        file_size_mb = 0.0
        if os.path.exists(output_path):
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            try:
                from pydub.utils import mediainfo
                info = mediainfo(output_path)
                duration_secs = float(info.get("duration", 0))
            except Exception:
                pass

        log.info(
            "MP3 exportado: %s — Duración: %.1f min, Tamaño: %.1f MB",
            output_path,
            duration_secs / 60,
            file_size_mb,
        )

        return output_path

    @staticmethod
    def _chunk_ends_sentence(text: str) -> bool:
        """
        Determina si un chunk termina en puntuación fuerte (punto, cierre de
        exclamación/interrogación, puntos suspensivos, comillas de cierre
        tras punto).

        Si el chunk NO termina en puntuación fuerte significa que su texto
        continúa en el siguiente chunk y NO debe insertarse silencio.
        """
        stripped = text.rstrip()
        if not stripped:
            return True  # chunk vacío → conservador: sí pausa
        # Último carácter significativo
        last = stripped[-1]
        return last in '.!?…"\u2019\u201d»)'

    def cleanup_temp_files(self, audio_paths: list[str]) -> None:
        """Elimina archivos temporales de audio y la lista concat."""
        for path in audio_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as e:
                log.warning("No se pudo eliminar %s: %s", path, e)
                
        # Remove concat.txt if it exists
        if audio_paths:
            temp_dir = os.path.dirname(audio_paths[0])
            concat_path = os.path.join(temp_dir, "concat.txt")
            if os.path.exists(concat_path):
                try:
                    os.remove(concat_path)
                except OSError:
                    pass
