import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from audiobook_gen.config import TTSConfig
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.core.tts_engine import EdgeTTSEngine, SAPIEngine, create_tts_engine


def test_create_tts_engine_uses_config_voice_by_default():
    config = TTSConfig(engine="edge", voice="es-ES-ElviraNeural")

    engine = create_tts_engine(config)

    assert isinstance(engine, EdgeTTSEngine)
    assert engine.get_voice_name() == "es-ES-ElviraNeural"


def test_create_tts_engine_accepts_voice_override():
    config = TTSConfig(engine="edge", voice="es-ES-ElviraNeural")

    engine = create_tts_engine(config, voice_id="es-ES-AlvaroNeural")

    assert engine.get_voice_name() == "es-ES-AlvaroNeural"


def test_create_tts_engine_sapi():
    config = TTSConfig(engine="sapi")

    with patch("pyttsx3.init"):
        engine = create_tts_engine(config, voice_id="System Default")

    assert isinstance(engine, SAPIEngine)


def test_edge_tts_synthesize_passes_voice_controls():
    config = TTSConfig(
        voice="es-ES-AlvaroNeural",
        rate="+10%",
        pitch="+5Hz",
        volume="-5%",
    )
    engine = EdgeTTSEngine(config, "es-ES-AlvaroNeural")
    chunk = TextChunk(text="Hola mundo", index=0)
    output_path = "test.mp3"

    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()

    def run_coro(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with patch("edge_tts.Communicate", return_value=mock_communicate) as communicate:
        with patch("asyncio.run", side_effect=run_coro):
            engine.synthesize(chunk, output_path)

    communicate.assert_called_with(
        "Hola mundo",
        voice="es-ES-AlvaroNeural",
        rate="+10%",
        pitch="+5Hz",
        volume="-5%",
    )
    mock_communicate.save.assert_called_with(output_path)


def test_edge_tts_empty_text_generates_silence():
    config = TTSConfig(voice="es-ES-AlvaroNeural")
    engine = EdgeTTSEngine(config, "es-ES-AlvaroNeural")
    chunk = TextChunk(text="   ", index=0)

    with patch("audiobook_gen.core.tts_engine.AudioSegment.silent") as mock_silent:
        mock_audio = MagicMock()
        mock_silent.return_value = mock_audio

        engine.synthesize(chunk, "silence.mp3")

    mock_silent.assert_called_with(duration=500)
    mock_audio.export.assert_called_with("silence.mp3", format="mp3")


def test_kokoro_missing_model_error_is_actionable():
    config = TTSConfig(engine="kokoro", voice="es_alex")

    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(RuntimeError, match="Kokoro offline model is not installed"):
            create_tts_engine(config)
