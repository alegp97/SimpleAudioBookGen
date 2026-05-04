import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from audiobook_gen.core.pdf_extractor import PDFExtractor, ExtractionResult, PageContent

@pytest.fixture
def mock_fitz_doc():
    doc = MagicMock()
    doc.metadata = {"title": "Test Title", "author": "Test Author"}
    doc.__len__.return_value = 2
    
    # Mock de páginas
    page1 = MagicMock()
    page1.get_text.return_value = "Este es un texto suficientemente largo para que no parezca un PDF escaneado. " * 20
    
    page2 = MagicMock()
    page2.get_text.return_value = "Aquí hay más contenido de prueba para la segunda página del documento. " * 20
    
    doc.__iter__.return_value = [page1, page2]
    return doc

def test_extract_success(mock_fitz_doc):
    extractor = PDFExtractor()
    
    with patch("fitz.open", return_value=mock_fitz_doc):
        # Crear un archivo dummy para que pase el check de exists()
        dummy_path = Path("test.pdf")
        with patch.object(Path, "exists", return_value=True):
            result = extractor.extract(dummy_path)
            
            assert result.metadata.total_pages == 2
            assert result.metadata.title == "Test Title"
            assert len(result.pages) == 2
            assert "texto suficientemente largo" in result.pages[0].text

def test_extract_scanned_pdf_fallback(mock_fitz_doc):
    extractor = PDFExtractor()
    # Usar un umbral muy alto para que cualquier texto parezca escaneado
    extractor.SCANNED_THRESHOLD = 10000 
    
    with patch("fitz.open", return_value=mock_fitz_doc):
        with patch.object(Path, "exists", return_value=True):
            # Mock de OCR para evitar que realmente intente hacer OCR
            with patch.object(extractor, "_extract_with_ocr") as mock_ocr:
                mock_ocr.return_value = [
                    PageContent(page_number=1, text="Texto OCR 1", is_ocr=True),
                    PageContent(page_number=2, text="Texto OCR 2", is_ocr=True)
                ]
                
                result = extractor.extract("test.pdf")
                
                assert result.metadata.is_scanned is True
                assert mock_ocr.called
                assert result.pages[0].text == "Texto OCR 1"

def test_extract_file_not_found():
    extractor = PDFExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("non_existent.pdf")

def test_extract_invalid_extension():
    extractor = PDFExtractor()
    # Crear un archivo real para que pase el check de exists()
    with patch.object(Path, "exists", return_value=True):
        with pytest.raises(ValueError, match="El archivo no es un PDF"):
            extractor.extract("test.txt")
