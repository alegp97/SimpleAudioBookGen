import pytest
from unittest.mock import MagicMock, patch
from audiobook_gen.core.audio_assembler import AudioAssembler
from audiobook_gen.core.text_segmenter import TextChunk
from audiobook_gen.config import AudioConfig

@pytest.fixture
def mock_audio_segment():
    segment = MagicMock()
    segment.__add__.return_value = segment
    segment.__iadd__.return_value = segment
    segment.apply_gain.return_value = segment
    segment.dBFS = -10.0
    segment.__len__.return_value = 5000 # 5 segundos
    return segment

def test_assemble_basic(mock_audio_segment):
    assembler = AudioAssembler()
    audio_paths = ["chunk1.mp3", "chunk2.mp3"]
    chunks = [
        TextChunk(text="T1", index=0),
        TextChunk(text="T2", index=1)
    ]
    output_path = "final.mp3"
    
    with patch("pydub.AudioSegment.empty", return_value=mock_audio_segment):
        with patch("pydub.AudioSegment.from_mp3", return_value=mock_audio_segment):
            with patch("os.path.getsize", return_value=1024*1024):
                result = assembler.assemble(audio_paths, chunks, output_path)
                
                assert result == output_path
                assert mock_audio_segment.export.called

def test_assemble_with_silences(mock_audio_segment):
    config = AudioConfig(silence_paragraph_ms=100, silence_chapter_ms=500)
    assembler = AudioAssembler(config)
    
    audio_paths = ["c1.mp3", "c2.mp3"]
    chunks = [
        TextChunk(text="C1", index=0, is_chapter_end=True),
        TextChunk(text="C2", index=1)
    ]
    
    with patch("pydub.AudioSegment.empty", return_value=mock_audio_segment):
        with patch("pydub.AudioSegment.from_mp3", return_value=mock_audio_segment):
            with patch("pydub.AudioSegment.silent") as mock_silent:
                mock_silent.return_value = mock_audio_segment
                with patch("os.path.getsize", return_value=100):
                    assembler.assemble(audio_paths, chunks, "out.mp3")
                    
                    # Debería haber llamado a silent con 500ms (fin capítulo)
                    mock_silent.assert_any_call(duration=500)

def test_normalize_volume(mock_audio_segment):
    config = AudioConfig(normalize_target_dbfs=-20.0)
    assembler = AudioAssembler(config)
    
    mock_audio_segment.dBFS = -10.0
    normalized = assembler._normalize_volume(mock_audio_segment)
    
    # -20 - (-10) = -10dB de ganancia
    mock_audio_segment.apply_gain.assert_called_with(-10.0)

def test_assemble_empty_list():
    assembler = AudioAssembler()
    with pytest.raises(ValueError, match="No hay fragmentos de audio"):
        assembler.assemble([], [], "out.mp3")
