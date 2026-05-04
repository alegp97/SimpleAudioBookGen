import pytest
from audiobook_gen.core.text_normalizer import TextNormalizer

def test_normalize_abbreviations():
    normalizer = TextNormalizer()
    # Forzar algunas reglas para el test si el yaml no las tiene o es distinto
    normalizer.abbreviations = {"pág.": "página", "Dr.": "doctor"}
    
    text = "Vea la pág. 5 del Dr. Smith."
    normalized = normalizer.normalize(text)
    
    assert "página" in normalized
    assert "doctor" in normalized
    assert "pág." not in normalized
    assert "Dr." not in normalized

def test_normalize_numbers():
    normalizer = TextNormalizer()
    
    # Test decimal
    text = "El valor es 3,14."
    normalized = normalizer.normalize(text)
    assert "tres coma catorce" in normalized
    
    # Test miles
    text = "Hay 1.500 personas."
    normalized = normalizer.normalize(text)
    assert "mil quinientos" in normalized

def test_normalize_acronyms():
    normalizer = TextNormalizer()
    normalizer.spell_acronyms = ["ONU", "EEUU"]
    
    text = "La ONU y EEUU."
    normalized = normalizer.normalize(text)
    assert "O-N-U" in normalized
    assert "E-E-U-U" in normalized

def test_normalize_symbols():
    normalizer = TextNormalizer()
    normalizer.symbols = {"%": " por ciento", "$": " dólares"}
    
    text = "Cuesta 50$ con un 5% de descuento."
    normalized = normalizer.normalize(text)
    assert "dólares" in normalized
    assert "por ciento" in normalized

def test_normalize_prosody():
    normalizer = TextNormalizer()
    
    text = "Hola... ¿cómo estás?? ¡Bien!!"
    normalized = normalizer.normalize(text)
    assert "..." in normalized
    assert normalized.count("?") == 1
    assert normalized.count("!") == 1
