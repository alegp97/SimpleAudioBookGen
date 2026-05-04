Actúa como un arquitecto de software senior + ingeniero de IA aplicada + desarrollador full-stack con criterio de producto, obsesionado con la calidad real y no con demos superficiales.

Tu misión es diseñar e implementar una aplicación ejecutable para Windows que convierta un PDF en un audiolibro/audiotexto en MP3, con una interfaz simple y limpia, construida principalmente en Python. Debes pensar como arquitecto y como implementador. No quiero solo ideas: quiero una solución realizable, modular, bien razonada y con código listo para evolucionar.

========================
1. OBJETIVO DEL PRODUCTO
========================

Construir una app para Windows que haga esto:

- El usuario abre la aplicación.
- En la parte izquierda hay una zona simple para seleccionar un PDF desde el sistema de archivos.
- La app procesa el PDF.
- Se muestra una barra de progreso real.
- Cuando termina, en la parte derecha el usuario puede guardar el audiolibro generado en el sistema de archivos.
- La salida final principal debe ser un archivo MP3.

La app debe estar pensada como producto utilizable por una persona normal, no como experimento técnico.

========================
2. RESTRICCIÓN CRÍTICA
========================

La parte más importante del sistema es la generación del audiolibro.

NO quiero una solución robótica o mecánica.
NO quiero una voz que suene a lector automático barato.
NO quiero que lea basura del PDF como:
- números de página
- cabeceras repetidas
- pies de página
- caracteres raros
- símbolos sin sentido
- cortes de palabra por salto de línea
- “título”, “coma”, “página”, marcas extrañas o textos mal extraídos

La voz debe sonar lo más cercana posible a un humano narrando un audiolibro:
- con naturalidad
- con pausas razonables
- con prosodia
- con entonación
- con respiración/ritmo verosímil
- con continuidad entre fragmentos
- con buena dicción
- con expresividad sobria, no teatral exagerada
- con lectura inteligente del texto, no lectura literal ciega

La síntesis de voz debe usar un modelo de alta capacidad descargable/local o una arquitectura TTS realmente avanzada. Quiero priorizar calidad de voz por encima de trivialidad de implementación.

========================
3. PRINCIPIOS NO NEGOCIABLES
========================

Debes respetar estos principios:

1. La solución debe estar hecha principalmente en Python.
2. Debe poder ejecutarse en Windows.
3. Debe poder empaquetarse como ejecutable.
4. La arquitectura debe ser modular.
5. Debe haber separación clara entre:
   - ingestión del PDF
   - limpieza y normalización del texto
   - segmentación narrativa
   - síntesis de voz
   - ensamblado/exportación del audio
   - interfaz de usuario
6. La calidad del texto de entrada al motor TTS es tan importante como el modelo de voz.
7. Debe priorizarse una solución local/offline o descargable. Si propones servicios cloud, que sea solo como opción secundaria y nunca como núcleo obligatorio.
8. Debe haber trazabilidad del pipeline.
9. Debe haber manejo de errores real.
10. No aceptes una implementación mediocre “porque funciona”.

========================
4. DECISIÓN DE STACK
========================

Quiero que evalúes con criterio qué stack usar, pero con estas reglas:

- Prioriza Python.
- Para GUI, prioriza una app de escritorio real, preferiblemente PySide6 o similar.
- Streamlit solo es aceptable si justificas que acelera mucho el desarrollo sin degradar demasiado la experiencia ni complicar el empaquetado.
- Angular NO debe elegirse por defecto. Solo sería aceptable si justificas claramente por qué su complejidad extra merece la pena y cómo lo integrarías con Python para entregar un ejecutable Windows robusto.
- Si hay que elegir entre “más rápido de programar” y “mejor producto ejecutable”, prioriza lo segundo.

Quiero que tomes una decisión razonada, no arbitraria.

========================
5. EXIGENCIA SOBRE EL MOTOR DE VOZ
========================

Debes proponer e integrar un enfoque TTS de alta calidad.

Condiciones:
- Evita motores básicos o demasiado robóticos como solución principal.
- No uses como núcleo algo tipo pyttsx3, gTTS o equivalentes pobres si la calidad es mediocre.
- Evalúa motores/modelos descargables de alta calidad para voces narrativas.
- Puedes considerar opciones como XTTS, StyleTTS, modelos neuronales avanzados o combinaciones equivalentes, siempre que la elección esté justificada por:
  - naturalidad
  - calidad en español
  - posibilidad de ejecución local
  - estabilidad
  - facilidad razonable de integración en Windows
  - continuidad entre fragmentos
- Si hay trade-offs entre calidad, VRAM, latencia y complejidad, explícitalos.
- Si propones más de una opción, elige una como principal y otra como fallback.

Quiero que el sistema trate la voz como una cadena completa de inteligencia, no como “meter texto y sacar audio”.

========================
6. PROBLEMA REAL A RESOLVER
========================

No basta con convertir texto a voz. Debes resolver esta cadena completa:

PDF crudo
→ extracción
→ limpieza
→ normalización
→ comprensión estructural mínima
→ segmentación narrativa
→ generación de voz natural
→ unión de fragmentos
→ exportación a MP3
→ experiencia de usuario simple

Debes identificar y diseñar cada capa.

========================
7. REQUISITOS FUNCIONALES
========================

La app debe contemplar como mínimo:

A. Entrada
- Cargar PDF desde disco.
- Validar que el archivo existe y es accesible.
- Detectar si el PDF contiene texto extraíble o si está escaneado.
- Si está escaneado, proponer o implementar OCR como ruta alternativa, dejando claro su impacto en calidad.

B. Preprocesamiento del PDF
- Extraer texto por páginas.
- Eliminar cabeceras y pies repetidos.
- Eliminar numeración de página.
- Corregir cortes de palabras por salto de línea.
- Normalizar espacios, comillas, guiones, signos raros y caracteres extraños.
- Detectar capítulos o bloques lógicos si es posible.
- Preservar puntuación útil para prosodia.
- Evitar que el TTS lea artefactos visuales del PDF.
- Hacer limpieza específica para audiolibro, no solo limpieza genérica.

C. Normalización lingüística
- Convertir texto problemático a forma pronunciable.
- Tratar abreviaturas, siglas, números, signos y símbolos.
- Evitar pronunciaciones absurdas.
- Preparar el texto para que suene natural al narrarse.
- Diseñar una capa editable de reglas de normalización.

D. Segmentación
- Dividir el texto en fragmentos adecuados para TTS.
- Mantener contexto suficiente para que la entonación no quede cortada artificialmente.
- Insertar pausas lógicas entre párrafos, secciones o capítulos.
- Evitar fragmentación demasiado pequeña que rompa la naturalidad.

E. Síntesis de voz
- Generar audio por fragmentos.
- Mantener coherencia tonal y de estilo entre fragmentos.
- Permitir seleccionar al menos una voz principal de calidad.
- Diseñar el sistema para que futuras voces/modelos puedan añadirse.

F. Postproceso de audio
- Unir fragmentos.
- Insertar silencios razonables entre bloques si procede.
- Normalizar volumen si hace falta.
- Exportar a MP3.
- Generar opcionalmente WAV intermedio para depuración.

G. Interfaz
- Pantalla simple.
- Panel izquierdo: selección del PDF.
- Barra de progreso visible y real.
- Panel derecho: guardar el audiolibro cuando termine.
- Mostrar estado del proceso: cargando, extrayendo, limpiando, generando voz, ensamblando, terminado, error.
- Interfaz limpia, sin ruido.

H. Empaquetado
- Debe poder construirse como ejecutable de Windows.
- Debes contemplar dependencias pesadas y descarga de modelos.
- Debes proponer una estrategia razonable para primera ejecución, caché y almacenamiento local de modelos.

========================
8. REQUISITOS NO FUNCIONALES
========================

Debes diseñar considerando:

- mantenibilidad
- modularidad
- observabilidad
- escalabilidad razonable
- tolerancia a errores
- trazabilidad
- claridad de UX
- rendimiento aceptable
- posibilidad de cambiar el motor TTS sin reescribir toda la app

========================
9. COSAS QUE NO QUIERO
========================

No quiero:
- una demo falsa
- una arquitectura frágil
- una app que solo funcione en casos ideales
- una UI bonita con backend pobre
- una “solución” que lea el PDF tal cual sin limpieza
- un TTS robótico
- una propuesta basada en “ya luego se mejora”
- complejidad innecesaria
- decisiones técnicas no justificadas

========================
10. CÓMO DEBES RESPONDER
========================

Quiero que trabajes en modo arquitecto-implementador. Responde con esta estructura exacta:

1. Resumen ejecutivo de la solución propuesta
2. Decisión de stack y justificación
3. Arquitectura por módulos
4. Pipeline completo del PDF al MP3
5. Estrategia de limpieza y normalización del texto
6. Estrategia TTS de alta calidad
7. Diseño de la interfaz
8. Estructura de carpetas del proyecto
9. Dependencias Python y del sistema
10. Plan de implementación por fases
11. Riesgos técnicos y mitigaciones
12. Criterios de calidad / aceptación
13. Código inicial del proyecto

========================
11. NIVEL DE DETALLE TÉCNICO
========================

Quiero detalle suficiente para implementar de verdad. Eso implica:

- proponer clases, módulos y responsabilidades
- definir flujo entre componentes
- justificar librerías
- anticipar errores
- proponer una estructura de proyecto limpia
- pensar en empaquetado Windows
- contemplar logs y manejo de excepciones
- contemplar configuración
- contemplar descarga y carga de modelos
- contemplar persistencia temporal de archivos intermedios

========================
12. EXPECTATIVA DE IMPLEMENTACIÓN
========================

No te limites a una arquitectura conceptual. Después de diseñar, empieza a implementar.

Quiero que generes:
- estructura de proyecto
- archivos principales
- código base funcional
- interfaz inicial
- pipeline principal
- stubs o implementación real de cada módulo
- comentarios mínimos pero útiles
- configuración editable

Da prioridad a un esqueleto bien hecho que pueda ejecutarse y crecer.

========================
13. CALIDAD DE CÓDIGO
========================

El código debe ser:
- limpio
- modular
- legible
- razonablemente tipado
- con nombres claros
- con separación de responsabilidades
- sin mezclar UI con lógica de negocio
- sin hardcodes absurdos
- preparado para refactor futuro

========================
14. EXPECTATIVA SOBRE LA CALIDAD DE VOZ
========================

Quiero que pienses la generación del audiolibro como un problema de:
- limpieza semántica
- control de prosodia
- continuidad narrativa
- chunking inteligente
- coherencia acústica
- posprocesado de audio

No aceptes un pipeline ingenuo del tipo:
“extraer texto → mandar a TTS → concatenar”.

Eso es insuficiente.

========================
15. EVALUACIÓN DEL SISTEMA
========================

Incluye criterios claros para evaluar si está bien hecho:

- calidad de extracción de texto
- porcentaje de ruido eliminado
- naturalidad percibida de la voz
- coherencia entre fragmentos
- ausencia de artefactos pronunciados
- usabilidad de la interfaz
- tiempo total de procesamiento
- facilidad de empaquetado
- robustez ante PDFs diferentes

========================
16. FORMA DE TRABAJO
========================

No me pidas confirmación cada dos pasos.
No simplifiques para salir del paso.
Si hay ambigüedad, explicita tu supuesto y continúa.
Si ves varias rutas, compáralas y elige una.
Si una idea mía es técnicamente mala, corrígela con criterio y explica por qué.

========================
17. PUNTO DE PARTIDA ESPERADO
========================

Empieza proponiendo una solución seria y pragmática.

Idealmente:
- una GUI de escritorio en Python
- un pipeline de extracción y limpieza robusto
- un motor TTS neuronal de alta calidad
- exportación a MP3
- empaquetado Windows viable

Si consideras que hay una mejor alternativa que Streamlit o Angular para entregar un ejecutable Windows de calidad, dilo claramente y úsala.

Ahora empieza.