import pytest
from unittest.mock import MagicMock, patch
from audiobook_gen.pipeline import AudioBookPipeline, PipelineState, PipelineResult
from audiobook_gen.config import Settings
from audiobook_gen.core.pdf_extractor import ExtractionResult, PDFMetadata, PageContent
from audiobook_gen.core.text_cleaner import CleanedText
from audiobook_gen.core.text_segmenter import TextChunk

def test_pipeline_run_success():
    settings = Settings()
    progress_callback = MagicMock()
    pipeline = AudioBookPipeline(settings, progress_callback)
    
    # Mocks de componentes
    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = ExtractionResult(
        metadata=PDFMetadata(total_pages=1),
        pages=[PageContent(page_number=1, text="Texto")]
    )
    
    mock_cleaner = MagicMock()
    mock_cleaner.clean.return_value = CleanedText(raw_text="Texto limpio")
    
    mock_normalizer = MagicMock()
    mock_normalizer.normalize.return_value = "Texto normalizado"
    
    mock_segmenter = MagicMock()
    mock_segmenter.segment.return_value = [TextChunk(text="Chunk", index=0)]
    
    mock_tts = MagicMock()
    mock_tts.get_voice_name.return_value = "Voz"
    
    mock_assembler = MagicMock()
    
    with patch("audiobook_gen.pipeline.PDFExtractor", return_value=mock_extractor), \
         patch("audiobook_gen.pipeline.TextCleaner", return_value=mock_cleaner), \
         patch("audiobook_gen.pipeline.TextNormalizer", return_value=mock_normalizer), \
         patch("audiobook_gen.pipeline.TextSegmenter", return_value=mock_segmenter), \
         patch("audiobook_gen.pipeline.create_tts_engine", return_value=mock_tts), \
         patch("audiobook_gen.pipeline.AudioAssembler", return_value=mock_assembler), \
         patch("audiobook_gen.pipeline.Path.exists", return_value=True):
        
        result = pipeline.run("input.pdf", "output.mp3")
        
        assert result.success is True
        assert result.output_path == "output.mp3"
        assert progress_callback.called
        # Verificar que se llegó al estado DONE
        last_progress = progress_callback.call_args_list[-1][0][0]
        assert last_progress.state == PipelineState.DONE

def test_pipeline_cancellation():
    pipeline = AudioBookPipeline()
    
    with patch("audiobook_gen.pipeline.Path.exists", return_value=True):
        # Mock extractor que lanza InterruptedError al ser llamado
        mock_extractor = MagicMock()
        mock_extractor.extract.side_effect = InterruptedError("Cancelado")
        
        with patch("audiobook_gen.pipeline.PDFExtractor", return_value=mock_extractor):
            result = pipeline.run("input.pdf", "output.mp3")
            assert result.success is False
            assert "Cancelado" in result.error

def test_pipeline_error_handling():
    pipeline = AudioBookPipeline()
    
    with patch("audiobook_gen.pipeline.Path.exists", return_value=True):
        mock_extractor = MagicMock()
        mock_extractor.extract.side_effect = Exception("Algo falló")
        
        with patch("audiobook_gen.pipeline.PDFExtractor", return_value=mock_extractor):
            result = pipeline.run("input.pdf", "output.mp3")
            assert result.success is False
            assert "Algo falló" in result.error
