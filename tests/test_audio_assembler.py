from unittest.mock import MagicMock, patch

import pytest

from audiobook_gen.config import AudioConfig
from audiobook_gen.core.audio_assembler import AudioAssembler
from audiobook_gen.core.text_segmenter import TextChunk


@pytest.fixture
def mock_audio_segment():
    segment = MagicMock()
    segment.__add__.return_value = segment
    segment.__iadd__.return_value = segment
    segment.apply_gain.return_value = segment
    segment.dBFS = -10.0
    segment.__len__.return_value = 5000
    return segment


def test_assemble_exports_final_mp3(mock_audio_segment):
    assembler = AudioAssembler()
    chunks = [TextChunk(text="T1.", index=0), TextChunk(text="T2.", index=1)]

    with patch("audiobook_gen.core.audio_assembler.AudioSegment.empty", return_value=mock_audio_segment), \
         patch("audiobook_gen.core.audio_assembler.AudioSegment.from_file", return_value=mock_audio_segment), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=1024 * 1024):
        result = assembler.assemble(["chunk1.mp3", "chunk2.wav"], chunks, "final.mp3")

    assert result == "final.mp3"
    mock_audio_segment.export.assert_called_with("final.mp3", format="mp3", bitrate="192k")


def test_assemble_inserts_chapter_silence(mock_audio_segment):
    config = AudioConfig(silence_paragraph_ms=100, silence_chapter_ms=500)
    assembler = AudioAssembler(config)
    chunks = [
        TextChunk(text="C1.", index=0, is_chapter_end=True),
        TextChunk(text="C2.", index=1),
    ]

    with patch("audiobook_gen.core.audio_assembler.AudioSegment.empty", return_value=mock_audio_segment), \
         patch("audiobook_gen.core.audio_assembler.AudioSegment.from_file", return_value=mock_audio_segment), \
         patch("audiobook_gen.core.audio_assembler.AudioSegment.silent", return_value=mock_audio_segment) as mock_silent, \
         patch("os.path.exists", return_value=False):
        assembler.assemble(["c1.mp3", "c2.wav"], chunks, "out.mp3")

    mock_silent.assert_called_with(duration=500)


def test_normalize_volume(mock_audio_segment):
    config = AudioConfig(normalize_target_dbfs=-20.0)
    assembler = AudioAssembler(config)

    assembler._normalize_volume(mock_audio_segment)

    mock_audio_segment.apply_gain.assert_called_with(-10.0)


def test_assemble_empty_list():
    assembler = AudioAssembler()

    with pytest.raises(ValueError, match="No hay fragmentos de audio"):
        assembler.assemble([], [], "out.mp3")
