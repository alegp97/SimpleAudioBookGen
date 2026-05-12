# SimpleAudioBookGen: Documentación Técnica de Capacidades (Skills)

Este documento detalla la arquitectura, el funcionamiento interno y las capacidades de Inteligencia Artificial de **SimpleAudioBookGen**, una solución avanzada para la transformación de documentos PDF en audiolibros de alta fidelidad.

---

## 1. Resumen Ejecutivo
Desde una perspectiva de ingeniería de IA, SimpleAudioBookGen no es un simple conversor de texto a voz. Es un **pipeline de procesamiento de lenguaje natural (NLP) y síntesis neuronal** diseñado para resolver el problema de la "lectura mecánica". El sistema prioriza la prosodia, la naturalidad y la limpieza semántica, asegurando que el resultado final sea indistinguible de una narración humana profesional.

---

## 2. Arquitectura del Backend: El Motor de Inteligencia
El backend está construido sobre un pipeline modular que transforma datos no estructurados (PDF) en flujos de audio coherentes.

### A. Extracción y Visión Artificial (OCR)
- **Módulo:** `PDFExtractor`
- **Capacidad:** Identifica si un PDF es nativo (capas de texto) o escaneado (imágenes).
- **Tecnología:** Utiliza `PyMuPDF` para extracción de alta velocidad y `Tesseract OCR` como fallback para documentos escaneados, permitiendo la digitalización de libros físicos con alta precisión.

### B. Procesamiento de Lenguaje Natural (NLP) y Limpieza
- **Módulo:** `TextCleaner` y `TextNormalizer`
- **Skill:** Limpieza semántica profunda. A diferencia de otros sistemas, este motor:
    - Detecta y elimina artefactos de PDF (encabezados, pies de página, números de página repetidos).
    - Repara cortes de palabras por guiones al final de línea.
    - Une líneas de texto manteniendo la continuidad narrativa, evitando pausas artificiales en medio de frases.
    - **Normalización:** Convierte abreviaturas, siglas y números (vía `num2words`) a su forma fonética expandida.

### C. Segmentación Narrativa Inteligente
- **Módulo:** `TextSegmenter`
- **Skill:** Chunking contextual. Divide el texto en fragmentos (chunks) respetando los límites de oraciones y párrafos. Esto garantiza que el motor TTS mantenga la entonación correcta y no corte frases a la mitad.

### D. Síntesis de Voz Neuronal (TTS)
- **Módulo:** `TTSEngine`
- **Modelos Soportados:**
    1. **Edge-TTS:** Utiliza voces neuronales de Microsoft en la nube para una calidad premium superior.
    2. **Kokoro (Offline):** Integración de modelos ONNX de vanguardia para síntesis local de alta fidelidad con bajo consumo de recursos.
    3. **Piper:** Motor de síntesis ultrarrápido para dispositivos con recursos limitados.
    4. **SAPI5:** Fallback para compatibilidad total con el sistema operativo Windows.

---

## 3. Arquitectura del Frontend: UX Centrada en el Producto
La interfaz de usuario ha sido diseñada en **PySide6 (Qt for Python)**, siguiendo principios de diseño moderno y eficiencia operativa.

- **Diseño Premium:** Uso de hojas de estilo (QSS) para una estética oscura, moderna y profesional.
- **Asincronía Total:** El pipeline de IA corre en hilos separados (`QThread`), permitiendo que la interfaz permanezca reactiva mientras se procesan miles de palabras.
- **Feedback en Tiempo Real:** Barra de progreso ponderada que refleja con precisión cada fase (extracción, normalización, síntesis, ensamblado).
- **Modelos offline manuales:** Kokoro y Piper se detectan desde carpetas locales documentadas. El usuario instala los modelos manualmente; la app no descarga ni elimina voces.

---

## 4. Skills y Capacidades Técnicas Destacadas

| Capacidad | Descripción Técnica |
| :--- | :--- |
| **Prosodia Avanzada** | Inserción automática de silencios variables entre párrafos (200ms) y capítulos (1800ms) para un ritmo narrativo natural. |
| **Detección de Estructura** | Identificación automática de capítulos basada en patrones regex inteligentes para organizar el flujo narrativo. |
| **Ensamblado robusto** | Acepta fragmentos MP3/WAV mixtos, inserta pausas y reexporta un MP3 final homogéneo. |
| **Multi-idioma** | Soporte para más de 12 idiomas con catálogos de voces específicos por región y género. |
| **Portabilidad** | Preparado para ser empaquetado como un ejecutable `.exe` independiente mediante `PyInstaller`. |

---

## 5. Conclusión
SimpleAudioBookGen representa la convergencia entre el procesamiento de documentos tradicional y la IA aplicada moderna. Su arquitectura modular permite la evolución continua de sus "skills", permitiendo la integración de nuevos modelos de lenguaje o síntesis de voz a medida que la tecnología de IA avance.

**Ingeniería de Calidad | IA Narrativa | Experiencia de Usuario**
