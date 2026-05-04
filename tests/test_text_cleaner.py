import pytest
from audiobook_gen.core.text_cleaner import TextCleaner
from audiobook_gen.core.pdf_extractor import PageContent
from audiobook_gen.config import CleanerConfig

def test_detect_repeated_lines():
    config = CleanerConfig(header_footer_threshold=0.5)
    cleaner = TextCleaner(config)
    
    pages = [
        PageContent(text="Cabecera\nEste es el cuerpo único de la página uno que no debería repetirse.\nPie de página", page_number=1),
        PageContent(text="Cabecera\nAquí hay otro texto totalmente diferente para la página dos.\nPie de página", page_number=2),
        PageContent(text="Cabecera\nY un tercer bloque de texto distinto para la página tres.\nPie de página", page_number=3),
        PageContent(text="Distinto\nFinalmente un cuarto texto que no tiene nada que ver.\nPie de página", page_number=4),
    ]
    
    repeated = cleaner._detect_repeated_lines(pages)
    assert "Cabecera" in repeated
    assert "Pie de página" in repeated
    assert "Contenido de la página 1" not in repeated

def test_remove_page_numbers():
    cleaner = TextCleaner()
    text = "Texto normal\n1\nSigue el texto\n- 42 -\nPágina 123"
    cleaned = cleaner._remove_page_numbers(text)
    
    assert "1" not in cleaned.split("\n")
    assert "- 42 -" not in cleaned
    assert "Página 123" not in cleaned
    assert "Texto normal" in cleaned

def test_fix_hyphenated_words():
    cleaner = TextCleaner()
    text = "Esta es una pala-\nbra cortada."
    cleaned = cleaner._fix_hyphenated_words(text)
    assert "palabra" in cleaned
    assert "pala-" not in cleaned

def test_clean_pipeline():
    # Usar un umbral de 1.0 para que solo se borre lo que está en TODAS las páginas
    config = CleanerConfig(header_footer_threshold=1.0, min_line_length=0)
    cleaner = TextCleaner(config)
    pages = [
        PageContent(text="HEADER\nCAPÍTULO 1: INTRODUCCIÓN\nEste es el primer párrafo del libro que debe ser conservado.\nFOOTER", page_number=1),
        PageContent(text="HEADER\nEste es el segundo párrafo con más contenido para evitar filtros.\nFOOTER", page_number=2),
        PageContent(text="HEADER\nEste es el tercer párrafo que asegura que el texto es largo.\nFOOTER", page_number=3),
    ]
    
    result = cleaner.clean(pages)
    
    # Verificaciones
    assert "HEADER" not in result.full_text
    assert "FOOTER" not in result.full_text
    assert "INTRODUCCIÓN" in result.full_text
    assert len(result.chapters) == 1
    assert result.chapters[0].title == "CAPÍTULO 1: INTRODUCCIÓN"

def test_detect_chapters():
    cleaner = TextCleaner()
    # Contenido largo para evitar el filtro de duplicados por cercanía (50 chars)
    text = (
        "CAPÍTULO 1: PRIMERO\n" + ("A" * 60) + "\n" +
        "CAPÍTULO 2: SEGUNDO\n" + ("B" * 60)
    )
    pages = [PageContent(text=text, page_number=1)]
    
    chapters = cleaner._detect_chapters(text, pages)
    assert len(chapters) == 2
    assert chapters[0].title == "CAPÍTULO 1: PRIMERO"
    assert chapters[1].title == "CAPÍTULO 2: SEGUNDO"
