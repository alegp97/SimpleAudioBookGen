import pytest
from audiobook_gen.core.text_segmenter import TextSegmenter, TextChunk
from audiobook_gen.config import SegmenterConfig

def test_split_by_chapters():
    segmenter = TextSegmenter()
    text = "Intro\n\n[CAPÍTULO: Uno]\nContenido uno.\n\n[CAPÍTULO: Dos]\nContenido dos."
    sections = segmenter._split_by_chapters(text)
    
    assert len(sections) == 3
    assert sections[0][0] is None
    assert "Intro" in sections[0][1]
    assert sections[1][0] == "Uno"
    assert "Contenido uno." in sections[1][1]
    assert sections[2][0] == "Dos"

def test_split_paragraphs():
    segmenter = TextSegmenter()
    text = "Párrafo 1.\n\n  Párrafo 2.  \n\nPárrafo 3."
    paras = segmenter._split_paragraphs(text)
    assert len(paras) == 3
    assert paras[1] == "Párrafo 2."

def test_segment_long_paragraph():
    config = SegmenterConfig(max_chunk_chars=50, min_chunk_chars=10)
    segmenter = TextSegmenter(config)
    
    # Oraciones que superan los 50 caracteres combinadas
    text = "Esta es una oración corta. Esta es otra oración que hará que el chunk sea demasiado largo."
    chunks = segmenter.segment(text)
    
    assert len(chunks) >= 2
    assert all(len(ch.text) <= 100 for ch in chunks) # Margen por unión de oraciones
    assert chunks[0].text == "Esta es una oración corta."

def test_segment_pipeline():
    config = SegmenterConfig(max_chunk_chars=100, min_chunk_chars=10)
    segmenter = TextSegmenter(config)
    
    text = "[CAPÍTULO: Capítulo de Prueba]\nEste es el contenido del capítulo. Tiene varias oraciones. Queremos ver si se segmenta bien."
    chunks = segmenter.segment(text)
    
    assert len(chunks) > 0
    assert chunks[0].chapter == "Capítulo de Prueba"
    assert chunks[0].is_chapter_start is True
    assert chunks[-1].is_chapter_end is True

def test_min_chunk_chars():
    config = SegmenterConfig(max_chunk_chars=100, min_chunk_chars=50)
    segmenter = TextSegmenter(config)
    
    text = "Texto muy corto."
    chunks = segmenter.segment(text)
    
    # El texto es más corto que min_chunk_chars (50), debería ser filtrado si no se une a nada
    assert len(chunks) == 0
