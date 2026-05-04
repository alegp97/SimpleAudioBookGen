import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch, AsyncMock
from audiobook_gen.core.tts_engine import create_tts_engine, EdgeTTSEngine, SAPIEngine
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.config import TTSConfig

def test_create_tts_engine_edge():
    config = TTSConfig(engine="edge")
    with patch("edge_tts.Communicate"):
        engine = create_tts_engine(config)
        assert isinstance(engine, EdgeTTSEngine)

def test_create_tts_engine_sapi():
    config = TTSConfig(engine="sapi")
    with patch("pyttsx3.init"):
        engine = create_tts_engine(config)
        assert isinstance(engine, SAPIEngine)

def test_edge_tts_synthesize():
    config = TTSConfig(voice="es-ES-AlvaroNeural")
    engine = EdgeTTSEngine(config)
    chunk = TextChunk(text="Hola mundo", index=0)
    output_path = "test.mp3"
    
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    
    # Mock para que asyncio.run ejecute la corrutina de forma síncrona en el test
    def run_coro(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with patch("edge_tts.Communicate", return_value=mock_communicate):
        with patch("asyncio.run", side_effect=run_coro):
            with patch("audiobook_gen.core.tts_engine.log"): # Silenciar logs
                engine.synthesize(chunk, output_path)
                
                # Verificamos que se llamó a Communicate con los parámetros correctos
                import edge_tts
                edge_tts.Communicate.assert_called_with(
                    "Hola mundo",
                    voice="es-ES-AlvaroNeural",
                    rate="+0%",
                    pitch="+0Hz",
                    volume="+0%"
                )
                mock_communicate.save.assert_called_with(output_path)

def test_edge_tts_empty_text():
    engine = EdgeTTSEngine()
    chunk = TextChunk(text="   ", index=0)
    output_path = "silence.mp3"
    
    with patch("pydub.AudioSegment.silent") as mock_silent:
        mock_audio = MagicMock()
        mock_silent.return_value = mock_audio
        
        engine.synthesize(chunk, output_path)
        
        mock_silent.assert_called_with(duration=500)
        mock_audio.export.assert_called_with(output_path, format="mp3")
