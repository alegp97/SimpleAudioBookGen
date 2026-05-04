"""
Script de verificación del fix de pausas entre líneas.

Ejecutar desde C:\\Users\\EM2024007301\\Desktop\\AudioBookGen con:
    .venv\\Scripts\\python.exe test_pausas_fix.py
"""

import sys
import os

# Asegurarse de estar en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("TEST 1: _join_continuation_lines (text_cleaner)")
print("=" * 60)

from audiobook_gen.core.text_cleaner import TextCleaner

cleaner = TextCleaner()

# Caso real: "pe-\nrro" ya está reparado por _fix_hyphenated_words
# Aquí testamos líneas que continúan sin guión
casos = [
    (
        "y el perro se subio\na la silla y empezo\na ladrar.\n\nEsto es otro parrafo.",
        "y el perro se subio a la silla y empezo a ladrar.\n\nEsto es otro parrafo.",
        "Líneas de continuación deben unirse, párrafos separados por \\n\\n preservarse"
    ),
    (
        "Era una noche tranquila\ny oscura, sin luna.\n\nAl dia siguiente llovio.",
        "Era una noche tranquila y oscura, sin luna.\n\nAl dia siguiente llovio.",
        "Línea media unida, párrafo nuevo preservado"
    ),
    (
        "Termino con punto.\nEsta es nueva oracion.",
        "Termino con punto.\nEsta es nueva oracion.",
        "Línea que termina en punto NO debe unirse"
    ),
]

all_ok = True
for entrada, esperado, desc in casos:
    resultado = cleaner._join_continuation_lines(entrada)
    ok = resultado == esperado
    all_ok = all_ok and ok
    print(f"\n  [{('OK' if ok else 'FALLO')}] {desc}")
    if not ok:
        print(f"    ENTRADA  : {repr(entrada)}")
        print(f"    ESPERADO : {repr(esperado)}")
        print(f"    OBTENIDO : {repr(resultado)}")

print()
print("=" * 60)
print("TEST 2: _chunk_ends_sentence (audio_assembler)")
print("=" * 60)

from audiobook_gen.core.audio_assembler import AudioAssembler

casos_pausa = [
    # (texto,              debe_pausar, descripcion)
    ("el pe",             False,  "mitad de palabra → NO pausa"),
    ("el perro.",         True,   "termina en punto → SÍ pausa"),
    ("subio a la silla",  False,  "sin puntuación final → NO pausa"),
    ("ladrar!",           True,   "termina en ! → SÍ pausa"),
    ("continua con",      False,  "sin puntuación → NO pausa"),
    ("termina...",        True,   "puntos suspensivos → SÍ pausa"),
    ("dijo: \"ven\"",    True,   "termina en comilla → SÍ pausa"),
    ("",                  True,   "vacío → SÍ pausa (conservador)"),
]

print()
for texto, esperado, desc in casos_pausa:
    resultado = AudioAssembler._chunk_ends_sentence(texto)
    ok = resultado == esperado
    all_ok = all_ok and ok
    print(f"  [{'OK' if ok else 'FALLO'}] {desc}")
    if not ok:
        print(f"    texto={repr(texto)} esperado={esperado} obtenido={resultado}")

print()
print("=" * 60)
if all_ok:
    print("✅ TODOS LOS TESTS PASAN — el fix está correcto")
else:
    print("❌ HAY TESTS FALLANDO — revisar la lógica")
print("=" * 60)
