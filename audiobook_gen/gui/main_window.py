"""
Ventana principal de AudioBookGen (Versión 14:15 + Menús Detallados).
Diseño moderno, premium y en español.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QProgressBar, QPushButton,
    QVBoxLayout, QWidget, QComboBox, QGroupBox, QLineEdit,
    QGridLayout, QSpacerItem, QSizePolicy
)

from audiobook_gen.config import Settings
from audiobook_gen.pipeline import AudioBookPipeline, PipelineProgress, PipelineResult, PipelineState
from audiobook_gen.utils.logger import get_logger
from audiobook_gen.voices import (
    EDGE_VOICES, KOKORO_VOICES, PIPER_VOICES, LANGUAGE_ORDER,
    is_kokoro_installed, is_piper_voice_installed, SAMPLE_TEXTS
)

log = get_logger("main_window")

# Estilos Modernos Premium
MODERN_STYLESHEET = """
QMainWindow { background-color: #0f0f12; }
QWidget { color: #f0f0f5; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
QGroupBox {
    background-color: #1a1a24;
    border: 1px solid #2d2d3d;
    border-radius: 12px;
    margin-top: 25px;
    padding-top: 20px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 15px;
    color: #4d7cff;
    font-size: 14px;
}
QPushButton {
    background-color: #3d5afe;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 15px;
    font-weight: bold;
}
QPushButton:hover { background-color: #536dfe; }
QPushButton#secondaryBtn { background-color: #2d2d3d; color: #b0b0c8; }
QPushButton#secondaryBtn:hover { background-color: #3d3d4d; color: white; }
QPushButton#accentBtn { background-color: #00c853; }
QPushButton#dangerBtn { background-color: #ff5252; }
QLineEdit, QComboBox {
    background-color: #12121a;
    border: 1px solid #2d2d3d;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
}
QProgressBar {
    background-color: #12121a;
    border: 1px solid #2d2d3d;
    border-radius: 10px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3d5afe, stop:1 #8c9eff);
    border-radius: 9px;
}
QMessageBox {
    background-color: #1a1a24;
}
QMessageBox QLabel {
    color: #f0f0f5;
}
QMessageBox QPushButton {
    min-width: 80px;
    background-color: #3d5afe;
}
QLabel#headerTitle { font-size: 26px; font-weight: bold; color: white; }
QLabel#headerSubtitle { color: #707085; font-size: 14px; }
QLabel#statusText { color: #8c9eff; font-weight: bold; }
"""

class PipelineWorker(QThread):
    progress = Signal(object)
    finished = Signal(object)
    def __init__(self, pipeline: AudioBookPipeline, pdf_path: str, output_path: str):
        super().__init__()
        self.pipeline, self.pdf_path, self.output_path = pipeline, pdf_path, output_path
    def run(self):
        self.pipeline._progress_callback = lambda p: self.progress.emit(p)
        self.finished.emit(self.pipeline.run(self.pdf_path, self.output_path))

class AudioPreviewWorker(QThread):
    finished = Signal(bool, str)
    def __init__(self, settings, voice_id, engine, lang):
        super().__init__()
        self.settings, self.voice_id, self.engine, self.lang = settings, voice_id, engine, lang
    def run(self):
        from audiobook_gen.core.tts_engine import create_tts_engine
        from audiobook_gen.core.text_segmenter import TextChunk
        try:
            config = self.settings.tts
            config.engine, config.voice = self.engine, self.voice_id
            tts = create_tts_engine(config, voice_id=self.voice_id)
            sample = SAMPLE_TEXTS.get(self.lang, SAMPLE_TEXTS["Spanish"])
            temp_path = os.path.join(self.settings.temp_dir, f"preview_{self.voice_id}.mp3")
            tts.synthesize(TextChunk(index=0, text=sample), temp_path)
            self.finished.emit(True, temp_path)
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.setAcceptDrops(True)
        self._pdf_path = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.setWindowTitle("SimpleAudioBookGen — Conversor Premium")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(MODERN_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Encabezado Detallado
        header = QVBoxLayout()
        title = QLabel("SimpleAudioBookGen")
        title.setObjectName("headerTitle")
        subtitle = QLabel("Crea audiolibros de alta calidad con voces neuronales IA a partir de tus documentos PDF")
        subtitle.setObjectName("headerSubtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        main_layout.addLayout(header)

        # Cuerpo Principal: Dos Columnas
        content_row = QHBoxLayout()
        content_row.setSpacing(25)

        # Columna Izquierda: Entrada y Destino
        left_col = QVBoxLayout()
        
        # Paso 1: Selección de Archivo
        input_group = QGroupBox("📥 PASO 1: SELECCIONAR ORIGEN")
        input_group.setToolTip("Elige el archivo PDF que deseas convertir a voz")
        input_layout = QVBoxLayout(input_group)
        self.btn_select_pdf = QPushButton("Seleccionar Archivo PDF")
        self.btn_select_pdf.setMinimumHeight(45)
        self.lbl_pdf_path = QLabel("Arrastra el PDF aquí o haz clic arriba")
        self.lbl_pdf_path.setAlignment(Qt.AlignCenter)
        self.lbl_pdf_path.setStyleSheet("color: #707085; border: 2px dashed #2d2d3d; border-radius: 10px; padding: 20px;")
        input_layout.addWidget(self.btn_select_pdf)
        input_layout.addWidget(self.lbl_pdf_path)
        left_col.addWidget(input_group)

        # Paso 2: Destino y Calidad
        output_group = QGroupBox("📤 PASO 2: DESTINO Y SALIDA")
        output_group.setToolTip("Configura dónde se guardará el audio y su calidad")
        output_layout = QGridLayout(output_group)
        output_layout.addWidget(QLabel("Guardar audio en:"), 0, 0)
        self.edit_output = QLineEdit()
        self.edit_output.setPlaceholderText("Selecciona la ruta de destino...")
        self.btn_browse_output = QPushButton("...")
        self.btn_browse_output.setFixedWidth(40)
        self.btn_browse_output.setObjectName("secondaryBtn")
        output_layout.addWidget(self.edit_output, 0, 1)
        output_layout.addWidget(self.btn_browse_output, 0, 2)
        
        output_layout.addWidget(QLabel("Calidad (Bitrate):"), 1, 0)
        self.combo_bitrate = QComboBox()
        self.combo_bitrate.addItems(["64k", "128k", "192k", "256k", "320k"])
        self.combo_bitrate.setCurrentText("192k")
        output_layout.addWidget(self.combo_bitrate, 1, 1, 1, 2)
        left_col.addWidget(output_group)
        left_col.addStretch()
        content_row.addLayout(left_col, 1)

        # Columna Derecha: Configuración de Voz
        right_col = QVBoxLayout()
        tts_group = QGroupBox("🎙️ PASO 3: CONFIGURACIÓN DE VOZ")
        tts_group.setToolTip("Elige el motor, el idioma y la voz que más te guste")
        tts_layout = QVBoxLayout(tts_group)
        
        tts_layout.addWidget(QLabel("Motor de Síntesis:"))
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["Edge-TTS (Online)", "Kokoro (Offline)", "Piper (Offline)", "SAPI5 (Local)"])
        tts_layout.addWidget(self.combo_engine)
        
        tts_layout.addWidget(QLabel("Idioma del Documento:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(LANGUAGE_ORDER)
        tts_layout.addWidget(self.combo_lang)
        
        tts_layout.addWidget(QLabel("Seleccionar Voz:"))
        voice_row = QHBoxLayout()
        self.combo_voice = QComboBox()
        self.btn_preview = QPushButton("▶ Escuchar")
        self.btn_preview.setObjectName("secondaryBtn")
        self.btn_preview.setToolTip("Reproduce una muestra de la voz seleccionada")
        voice_row.addWidget(self.combo_voice, 1)
        voice_row.addWidget(self.btn_preview)
        tts_layout.addLayout(voice_row)
        
        self.btn_manage_voices = QPushButton("Gestionar Voces Offline (Instalar/Borrar)")
        self.btn_manage_voices.setObjectName("secondaryBtn")
        tts_layout.addWidget(self.btn_manage_voices)
        tts_layout.addStretch()
        
        # Botón de Acción Principal
        self.btn_generate = QPushButton("INICIAR CONVERSIÓN A AUDIOLIBRO")
        self.btn_generate.setObjectName("accentBtn")
        self.btn_generate.setMinimumHeight(60)
        self.btn_generate.setEnabled(False)
        tts_layout.addWidget(self.btn_generate)
        
        self.btn_cancel = QPushButton("DETENER PROCESO")
        self.btn_cancel.setObjectName("dangerBtn")
        self.btn_cancel.setMinimumHeight(50)
        self.btn_cancel.setVisible(False)
        tts_layout.addWidget(self.btn_cancel)

        right_col.addWidget(tts_group)
        content_row.addLayout(right_col, 1)
        main_layout.addLayout(content_row)

        # Panel de Progreso
        progress_group = QGroupBox("📊 ESTADO DEL PROCESO")
        progress_layout = QVBoxLayout(progress_group)
        self.lbl_status = QLabel("Listo para comenzar")
        self.lbl_status.setObjectName("statusText")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.lbl_detail = QLabel("Por favor, selecciona un archivo PDF para analizar su contenido.")
        progress_layout.addWidget(self.lbl_status)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.lbl_detail)
        main_layout.addWidget(progress_group)

    def _connect_signals(self) -> None:
        self.btn_select_pdf.clicked.connect(self._on_select_pdf)
        self.btn_browse_output.clicked.connect(self._on_browse_output)
        self.combo_lang.currentIndexChanged.connect(self._populate_voices)
        self.combo_engine.currentIndexChanged.connect(self._populate_voices)
        self.btn_preview.clicked.connect(self._on_preview)
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_manage_voices.clicked.connect(self._on_manage_voices)
        self._populate_voices()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(".pdf"): self._load_pdf(path)

    def _on_select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "Archivos PDF (*.pdf)")
        if path: self._load_pdf(path)

    def _load_pdf(self, path):
        self._pdf_path = path
        self.lbl_pdf_path.setText(Path(path).name)
        self.lbl_pdf_path.setStyleSheet("color: #00c853; border: 2px solid #00c853; border-radius: 10px; padding: 20px; font-weight: bold;")
        if not self.edit_output.text(): self.edit_output.setText(str(Path(path).with_suffix(".mp3")))
        self.btn_generate.setEnabled(True)
        self.lbl_status.setText("Documento analizado correctamente")

    def _on_browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar como", self.edit_output.text(), "Audio MP3 (*.mp3)")
        if path: self.edit_output.setText(path)

    def _populate_voices(self):
        self.combo_voice.clear()
        lang, eng_idx = self.combo_lang.currentText(), self.combo_engine.currentIndex()
        if eng_idx == 0: voices = EDGE_VOICES.get(lang, [])
        elif eng_idx == 1: voices = KOKORO_VOICES.get(lang, [])
        elif eng_idx == 2: voices = PIPER_VOICES.get(lang, [])
        else: self.combo_voice.addItem("Voz predeterminada del sistema", "sapi"); return
        for v in voices:
            label = v.display_name
            if eng_idx == 1 and not is_kokoro_installed(): label += " [No instalado]"
            elif eng_idx == 2 and not is_piper_voice_installed(v.id): label += " [No instalado]"
            self.combo_voice.addItem(label, v.id)

    def _on_preview(self):
        v_id, eng_idx = self.combo_voice.currentData(), self.combo_engine.currentIndex()
        engine = ["edge", "kokoro", "piper", "sapi"][eng_idx]
        if engine == "kokoro" and not is_kokoro_installed(): return
        if engine == "piper" and not is_piper_voice_installed(v_id): return
        self.btn_preview.setEnabled(False)
        self.btn_preview.setText("⌛ Generando...")
        self.preview_worker = AudioPreviewWorker(self.settings, v_id, engine, self.combo_lang.currentText())
        self.preview_worker.finished.connect(self._on_preview_done)
        self.preview_worker.start()

    def _on_preview_done(self, ok, res):
        self.btn_preview.setEnabled(True)
        self.btn_preview.setText("▶ Escuchar")
        if ok: self.player.stop(); self.player.setSource(QUrl.fromLocalFile(os.path.abspath(res))); self.player.play()
        else: QMessageBox.critical(self, "Error", f"Fallo en la muestra: {res}")

    def _on_generate(self):
        self.settings.tts.engine = ["edge", "kokoro", "piper", "sapi"][self.combo_engine.currentIndex()]
        self.settings.tts.voice = self.combo_voice.currentData()
        self.btn_generate.setVisible(False); self.btn_cancel.setVisible(True)
        self.pipeline = AudioBookPipeline(self.settings)
        self.worker = PipelineWorker(self.pipeline, self._pdf_path, self.edit_output.text())
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, p):
        self.progress_bar.setValue(int(p.progress * 1000))
        self.lbl_status.setText(p.message); self.lbl_detail.setText(p.detail)

    def _on_finished(self, res):
        self.btn_generate.setVisible(True); self.btn_cancel.setVisible(False)
        if res.success: QMessageBox.information(self, "Éxito", f"Audiolibro listo en:\n{res.output_path}")
        else: QMessageBox.critical(self, "Error", f"Error: {res.error}")

    def _on_cancel(self):
        if self.pipeline: self.pipeline.cancel()
        self.lbl_status.setText("Cancelando proceso...")

    def _on_manage_voices(self):
        from audiobook_gen.gui.voice_manager import VoiceManagerDialog
        dlg = VoiceManagerDialog(self); dlg.voices_changed.connect(self._populate_voices); dlg.exec()
