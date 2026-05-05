"""
Gestor de Voces Premium para AudioBookGen.
Diseño moderno, oscuro y con mejores descripciones.
"""

from __future__ import annotations

import os
import shutil
import urllib.request
import ssl
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QWidget,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame
)

from audiobook_gen.voices import (
    KOKORO_MODEL_INFO, PIPER_VOICES,
    is_kokoro_installed, is_piper_voice_installed,
    kokoro_model_dir, piper_model_dir, LANGUAGE_ORDER
)

# Estilos Premium para el Gestor de Voces
VOICE_MANAGER_STYLESHEET = """
QDialog { background-color: #0f0f12; }
QWidget { color: #f0f0f5; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

QLabel#titleLabel { font-size: 20px; font-weight: bold; color: white; margin-bottom: 5px; }
QLabel#descLabel { color: #707085; font-size: 12px; margin-bottom: 10px; }

QTableWidget {
    background-color: #1a1a24;
    border: 1px solid #2d2d3d;
    border-radius: 8px;
    gridline-color: #2d2d3d;
    selection-background-color: #3d5afe;
}

QHeaderView::section {
    background-color: #12121a;
    color: #4d7cff;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}

QPushButton {
    background-color: #3d5afe;
    color: white;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: bold;
}
QPushButton:hover { background-color: #536dfe; }
QPushButton#dangerBtn { background-color: #ff5252; }
QPushButton#dangerBtn:hover { background-color: #ff1744; }
QPushButton#closeBtn { background-color: #2d2d3d; color: #b0b0c8; }

QProgressBar {
    background-color: #12121a;
    border: 1px solid #2d2d3d;
    border-radius: 8px;
    text-align: center;
    height: 20px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3d5afe, stop:1 #8c9eff);
    border-radius: 7px;
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
QComboBox {
    background-color: #12121a;
    border: 1px solid #2d2d3d;
    border-radius: 6px;
    padding: 6px;
}
"""

class DownloadWorker(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, url: str, dest: Path):
        super().__init__()
        self.url, self.dest = url, dest

    def run(self):
        try:
            self.dest.parent.mkdir(parents=True, exist_ok=True)
            ctx = ssl._create_unverified_context()
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            
            def report(count, size, total):
                if total > 0: self.progress.emit(int(count * size * 100 / total))
            
            urllib.request.urlretrieve(self.url, str(self.dest), reporthook=report)
            self.finished.emit(True, str(self.dest))
        except Exception as e:
            self.finished.emit(False, str(e))

class VoiceManagerDialog(QDialog):
    voices_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestor de Voces Offline")
        self.setMinimumSize(750, 550)
        self.setStyleSheet(VOICE_MANAGER_STYLESHEET)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Encabezado
        header = QVBoxLayout()
        title = QLabel("📥 Biblioteca de Voces Offline")
        title.setObjectName("titleLabel")
        desc = QLabel("Descarga modelos de alta calidad para generar audio sin conexión a Internet.")
        desc.setObjectName("descLabel")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # Filtros
        filter_row = QHBoxLayout()
        filter_row.setSpacing(20)
        
        engine_box = QVBoxLayout()
        engine_box.addWidget(QLabel("Motor TTS:"))
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["Kokoro (V1.0)", "Piper (Local)"])
        self.combo_engine.currentIndexChanged.connect(self._load_data)
        engine_box.addWidget(self.combo_engine)
        filter_row.addLayout(engine_box)
        
        lang_box = QVBoxLayout()
        lang_box.addWidget(QLabel("Idioma del modelo:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(LANGUAGE_ORDER)
        self.combo_lang.currentIndexChanged.connect(self._load_data)
        lang_box.addWidget(self.combo_lang)
        filter_row.addLayout(lang_box)
        
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Tabla de Voces
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nombre de la Voz", "Estado", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 150)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Estado de Descarga
        self.download_panel = QFrame()
        self.download_panel.setStyleSheet("background-color: #12121a; border-radius: 10px; padding: 10px;")
        self.download_panel.setVisible(False)
        dp_layout = QVBoxLayout(self.download_panel)
        
        self.lbl_status = QLabel("Preparando descarga...")
        self.lbl_status.setStyleSheet("color: #8c9eff; font-weight: bold;")
        dp_layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        dp_layout.addWidget(self.progress_bar)
        layout.addWidget(self.download_panel)

        # Botones Inferiores
        footer = QHBoxLayout()
        footer.addStretch()
        self.btn_close = QPushButton("Cerrar Gestor")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setMinimumWidth(120)
        self.btn_close.clicked.connect(self.accept)
        footer.addWidget(self.btn_close)
        layout.addLayout(footer)

    def _load_data(self):
        self.table.setRowCount(0)
        engine_idx = self.combo_engine.currentIndex()
        lang = self.combo_lang.currentText()

        if engine_idx == 0: # Kokoro
            installed = is_kokoro_installed()
            self._add_row("🧠 Modelo Base Kokoro v1.0", installed, "kokoro_base", "Modelo universal (requerido para todas las voces Kokoro)")
        else: # Piper
            voices = PIPER_VOICES.get(lang, [])
            for v in voices:
                installed = is_piper_voice_installed(v.id)
                desc = f"Voz {v.gender} ({v.locale})"
                self._add_row(f"🎙️ {v.display_name}", installed, v.id, desc)

    def _add_row(self, name, installed, voice_id, description):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Columna 1: Nombre y descripción
        name_widget = QWidget()
        nw_layout = QVBoxLayout(name_widget)
        nw_layout.setContentsMargins(10, 5, 10, 5)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-weight: bold; color: white;")
        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet("font-size: 11px; color: #707085;")
        nw_layout.addWidget(lbl_name)
        nw_layout.addWidget(lbl_desc)
        self.table.setCellWidget(row, 0, name_widget)
        self.table.setRowHeight(row, 60)
        
        # Columna 2: Estado con emoji
        status_text = "✅ Instalado" if installed else "☁️ Disponible"
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignCenter)
        if installed: status_item.setForeground(Qt.green)
        self.table.setItem(row, 1, status_item)
        
        # Columna 3: Botón de acción
        btn = QPushButton("Descargar" if not installed else "Eliminar")
        if installed: btn.setObjectName("dangerBtn")
        btn.clicked.connect(lambda: self._on_action(voice_id, not installed))
        
        container = QWidget()
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(10, 5, 10, 5)
        c_layout.addWidget(btn)
        self.table.setCellWidget(row, 2, container)

    def _on_action(self, voice_id, is_download):
        if not is_download:
            confirm = QMessageBox.question(self, "Confirmar borrado", "¿Estás seguro de que quieres eliminar esta voz para liberar espacio?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if voice_id == "kokoro_base": shutil.rmtree(kokoro_model_dir(), ignore_errors=True)
                else:
                    (piper_model_dir() / f"{voice_id}.onnx").unlink(missing_ok=True)
                    (piper_model_dir() / f"{voice_id}.onnx.json").unlink(missing_ok=True)
                self._load_data()
                self.voices_changed.emit()
            return

        # Lógica de descarga
        if voice_id == "kokoro_base":
            tasks = [(KOKORO_MODEL_INFO["url"], kokoro_model_dir() / "kokoro-v1.0.onnx"),
                     (KOKORO_MODEL_INFO["voices_url"], kokoro_model_dir() / "voices-v1.0.bin")]
        else:
            v_info = None
            for lv in PIPER_VOICES.values():
                for v in lv:
                    if v.id == voice_id: v_info = v; break
            if not v_info: return
            tasks = [(v_info.model_url, piper_model_dir() / f"{voice_id}.onnx"),
                     (v_info.model_url + ".json", piper_model_dir() / f"{voice_id}.onnx.json")]

        self._tasks, self._current_task = tasks, 0
        self.download_panel.setVisible(True)
        self.btn_close.setEnabled(False)
        self._run_next_task()

    def _run_next_task(self):
        if self._current_task >= len(self._tasks):
            self.download_panel.setVisible(False)
            self.btn_close.setEnabled(True)
            QMessageBox.information(self, "¡Completado!", "La voz se ha instalado correctamente y ya puedes seleccionarla.")
            self._load_data()
            self.voices_changed.emit()
            return

        url, dest = self._tasks[self._current_task]
        self.lbl_status.setText(f"Descargando componente {self._current_task + 1} de {len(self._tasks)}: {dest.name}")
        self.worker = DownloadWorker(url, dest)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self._on_task_done)
        self.worker.start()

    def _on_task_done(self, ok, msg):
        if ok: self._current_task += 1; self._run_next_task()
        else:
            QMessageBox.critical(self, "Error de Red", f"No se pudo completar la descarga:\n{msg}")
            self.download_panel.setVisible(False)
            self.btn_close.setEnabled(True)
