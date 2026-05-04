"""
Main GUI window for SimpleAudioBookGen.

PySide6 window with a two-panel layout:
- Left:   PDF selection
- Right:  TTS options + save MP3
- Bottom: progress bar and status
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QGroupBox,
)

from audiobook_gen.config import Settings
from audiobook_gen.pipeline import AudioBookPipeline, PipelineProgress, PipelineResult, PipelineState


# ═══════════════════════════════════════════════════════════════
# Voice catalogue  (Edge-TTS neural voices, grouped by language)
# ═══════════════════════════════════════════════════════════════

# Each entry: (voice_id, display_label)
_VOICES_BY_LANG: dict[str, list[tuple[str, str]]] = {
    "Spanish": [
        ("es-ES-AlvaroNeural",   "es-ES-AlvaroNeural   — Spain · Male"),
        ("es-ES-ElviraNeural",   "es-ES-ElviraNeural   — Spain · Female"),
        ("es-MX-JorgeNeural",    "es-MX-JorgeNeural    — Mexico · Male"),
        ("es-MX-DaliaNeural",    "es-MX-DaliaNeural    — Mexico · Female"),
        ("es-AR-TomasNeural",    "es-AR-TomasNeural    — Argentina · Male"),
        ("es-CO-GonzaloNeural",  "es-CO-GonzaloNeural  — Colombia · Male"),
    ],
    "English": [
        ("en-US-AndrewNeural",   "en-US-AndrewNeural   — US · Male"),
        ("en-US-AriaNeural",     "en-US-AriaNeural     — US · Female"),
        ("en-US-GuyNeural",      "en-US-GuyNeural      — US · Male"),
        ("en-GB-RyanNeural",     "en-GB-RyanNeural     — UK · Male"),
        ("en-GB-SoniaNeural",    "en-GB-SoniaNeural    — UK · Female"),
        ("en-AU-WilliamNeural",  "en-AU-WilliamNeural  — Australia · Male"),
        ("en-IN-NeerjaNeural",   "en-IN-NeerjaNeural   — India · Female"),
    ],
    "French": [
        ("fr-FR-HenriNeural",              "fr-FR-HenriNeural              — France · Male"),
        ("fr-FR-DeniseNeural",             "fr-FR-DeniseNeural             — France · Female"),
        ("fr-FR-EloiseNeural",             "fr-FR-EloiseNeural             — France · Female"),
        ("fr-FR-RemyMultilingualNeural",   "fr-FR-RemyMultilingualNeural   — France · Male (Multilingual)"),
        ("fr-FR-VivienneMultilingualNeural","fr-FR-VivienneMultilingualNeural— France · Female (Multilingual)"),
        ("fr-BE-GerardNeural",             "fr-BE-GerardNeural             — Belgium · Male"),
        ("fr-BE-CharlineNeural",           "fr-BE-CharlineNeural           — Belgium · Female"),
        ("fr-CH-FabriceNeural",            "fr-CH-FabriceNeural            — Switzerland · Male"),
        ("fr-CH-ArianeNeural",             "fr-CH-ArianeNeural             — Switzerland · Female"),
        ("fr-CA-ThierryNeural",            "fr-CA-ThierryNeural            — Canada · Male"),
        ("fr-CA-SylvieNeural",             "fr-CA-SylvieNeural             — Canada · Female"),
        ("fr-CA-AntoineNeural",            "fr-CA-AntoineNeural            — Canada · Male"),
    ],
    "Italian": [
        ("it-IT-DiegoNeural",    "it-IT-DiegoNeural    — Italy · Male"),
    ],
    "German": [
        ("de-DE-ConradNeural",   "de-DE-ConradNeural   — Germany · Male"),
    ],
    "Russian": [
        ("ru-RU-DmitryNeural",   "ru-RU-DmitryNeural   — Russia · Male"),
    ],
    "Chinese": [
        ("zh-CN-YunxiNeural",    "zh-CN-YunxiNeural    — China · Male"),
    ],
    "Portuguese": [
        ("pt-PT-DuarteNeural",   "pt-PT-DuarteNeural   — Portugal · Male"),
        ("pt-BR-FranciscaNeural","pt-BR-FranciscaNeural— Brazil · Female"),
    ],
    "Arabic": [
        ("ar-EG-SalmaNeural",    "ar-EG-SalmaNeural    — Egypt · Female"),
        ("ar-SA-ZariyahNeural",  "ar-SA-ZariyahNeural  — Saudi Arabia · Female"),
        ("ar-MA-JamalNeural",    "ar-MA-JamalNeural    — Morocco · Male"),
    ],
    "Japanese": [
        ("ja-JP-KeitaNeural",    "ja-JP-KeitaNeural    — Japan · Male"),
    ],
    "Korean": [
        ("ko-KR-InJoonNeural",   "ko-KR-InJoonNeural   — Korea · Male"),
    ],
}

# Ordered list of language names for the filter combo
_LANGUAGE_ORDER = [
    "All Languages",
    "Spanish", "English", "French", "Italian",
    "German", "Russian", "Chinese", "Portuguese",
    "Arabic", "Japanese", "Korean",
]


def _all_voices() -> list[tuple[str, str]]:
    """Return every voice across all languages."""
    result: list[tuple[str, str]] = []
    for lang in _LANGUAGE_ORDER[1:]:          # skip "All Languages"
        result.extend(_VOICES_BY_LANG[lang])
    return result


# ═══════════════════════════════════════════════════════════════
# Background worker thread
# ═══════════════════════════════════════════════════════════════

class PipelineWorker(QThread):
    """Runs the audio pipeline in a background thread to keep the UI responsive."""

    progress = Signal(object)   # PipelineProgress
    finished = Signal(object)   # PipelineResult

    def __init__(self, pipeline: AudioBookPipeline, pdf_path: str, output_path: str):
        super().__init__()
        self.pipeline = pipeline
        self.pdf_path = pdf_path
        self.output_path = output_path

    def run(self):
        def on_progress(p: PipelineProgress):
            self.progress.emit(p)

        self.pipeline._progress_callback = on_progress
        result = self.pipeline.run(self.pdf_path, self.output_path)
        self.finished.emit(result)


# ═══════════════════════════════════════════════════════════════
# Stylesheet
# ═══════════════════════════════════════════════════════════════

DARK_STYLESHEET = """
QMainWindow {
    background-color: #13141f;
}

QWidget {
    color: #e0e0e8;
    font-family: "Segoe UI", "Arial", sans-serif;
}

QGroupBox {
    background-color: #1c1d30;
    border: 1px solid #35365a;
    border-radius: 12px;
    margin-top: 14px;
    padding: 20px 16px 16px 16px;
    font-size: 13px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #8fa8ff;
}

QPushButton {
    background-color: #3d4fc0;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #5060e0;
}

QPushButton:pressed {
    background-color: #2e3a9e;
}

QPushButton:disabled {
    background-color: #2a2b48;
    color: #555570;
}

QPushButton#cancelBtn {
    background-color: #b83232;
}

QPushButton#cancelBtn:hover {
    background-color: #d94444;
}

QPushButton#saveBtn {
    background-color: #28a855;
}

QPushButton#saveBtn:hover {
    background-color: #34cc6a;
}

QProgressBar {
    background-color: #1e1f38;
    border: 1px solid #35365a;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-weight: bold;
    min-height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #3d4fc0, stop: 1 #6a7fff
    );
    border-radius: 9px;
}

QLabel {
    color: #b0b0c8;
}

QLabel#titleLabel {
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
    letter-spacing: 1px;
}

QLabel#subtitleLabel {
    color: #666688;
    font-size: 12px;
}

QLabel#statusLabel {
    color: #8fa8ff;
    font-size: 14px;
    font-weight: bold;
}

QLabel#fileLabel {
    color: #76e09a;
    font-size: 12px;
    padding: 8px;
    background-color: #161726;
    border-radius: 6px;
    border: 1px solid #35365a;
}

QLabel#infoLabel {
    color: #666688;
    font-size: 11px;
}

QLabel#sectionLabel {
    color: #9090b8;
    font-size: 12px;
    font-weight: bold;
}

QComboBox {
    background-color: #1e1f38;
    color: #e0e0e8;
    border: 1px solid #35365a;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 22px;
}

QComboBox:hover {
    border-color: #5060e0;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e1f38;
    color: #e0e0e8;
    selection-background-color: #3d4fc0;
    border: 1px solid #35365a;
    outline: none;
}

QFrame#separator {
    background-color: #2a2b48;
    max-width: 1px;
}
"""


# ═══════════════════════════════════════════════════════════════
# Main window
# ═══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """Main window of SimpleAudioBookGen."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.pipeline: Optional[AudioBookPipeline] = None
        self.worker: Optional[PipelineWorker] = None
        self._pdf_path: Optional[str] = None
        self._output_path: Optional[str] = None

        self._setup_ui()
        self._connect_signals()

    # ── UI Construction ─────────────────────────────────────────

    def _setup_ui(self) -> None:
        """Build the user interface."""
        self.setWindowTitle("SimpleAudioBookGen — PDF to Audiobook")
        self.setMinimumSize(960, 540)
        self.resize(1060, 600)
        self.setStyleSheet(DARK_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)

        # ── Header ──
        title = QLabel("SimpleAudioBookGen")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Convert your PDF into a natural-voice mp3 audiobook")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        root.addWidget(subtitle)

        root.addSpacing(6)

        # ── Two-panel row ──
        panels = QHBoxLayout()
        panels.setSpacing(16)
        panels.addWidget(self._build_left_panel(), 1)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.VLine)
        panels.addWidget(sep)

        panels.addWidget(self._build_right_panel(), 1)
        root.addLayout(panels, 1)

        # ── Progress panel ──
        root.addWidget(self._build_progress_panel())

    def _build_left_panel(self) -> QGroupBox:
        """Left panel: PDF input."""
        group = QGroupBox("📄  Input — PDF")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        self.btn_select_pdf = QPushButton("Select PDF")
        self.btn_select_pdf.setMinimumHeight(44)
        layout.addWidget(self.btn_select_pdf)

        self.lbl_pdf_path = QLabel("No file selected")
        self.lbl_pdf_path.setObjectName("fileLabel")
        self.lbl_pdf_path.setWordWrap(True)
        layout.addWidget(self.lbl_pdf_path)

        self.lbl_pdf_info = QLabel("")
        self.lbl_pdf_info.setObjectName("infoLabel")
        self.lbl_pdf_info.setWordWrap(True)
        layout.addWidget(self.lbl_pdf_info)

        layout.addStretch()
        return group

    def _build_right_panel(self) -> QGroupBox:
        """Right panel: TTS options + save."""
        group = QGroupBox("🎧  Output — Audiobook")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Engine selector
        lbl_engine = QLabel("TTS Engine:")
        lbl_engine.setObjectName("sectionLabel")
        layout.addWidget(lbl_engine)

        self.combo_engine = QComboBox()
        self.combo_engine.addItems([
            "Edge-TTS  (Online · High quality)",
            "SAPI5     (Offline · System voice)",
        ])
        self.combo_engine.currentIndexChanged.connect(self._on_engine_changed)
        layout.addWidget(self.combo_engine)

        layout.addSpacing(4)

        # Language filter (Edge-TTS only)
        self.lbl_language = QLabel("Language:")
        self.lbl_language.setObjectName("sectionLabel")
        layout.addWidget(self.lbl_language)

        self.combo_language = QComboBox()
        self.combo_language.addItems(_LANGUAGE_ORDER)
        self.combo_language.currentIndexChanged.connect(self._on_language_changed)
        layout.addWidget(self.combo_language)

        # Voice selector
        self.lbl_voice = QLabel("Voice:")
        self.lbl_voice.setObjectName("sectionLabel")
        layout.addWidget(self.lbl_voice)

        self.combo_voice = QComboBox()
        self.combo_voice.setMinimumContentsLength(38)
        layout.addWidget(self.combo_voice)

        # Populate initial voice list
        self._populate_voices("All Languages")

        layout.addSpacing(8)

        # Generate button
        self.btn_generate = QPushButton("▶  Generate Audiobook")
        self.btn_generate.setMinimumHeight(44)
        self.btn_generate.setEnabled(False)
        layout.addWidget(self.btn_generate)

        # Cancel button (hidden until running)
        self.btn_cancel = QPushButton("✕  Cancel")
        self.btn_cancel.setObjectName("cancelBtn")
        self.btn_cancel.setMinimumHeight(36)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setVisible(False)
        layout.addWidget(self.btn_cancel)

        layout.addSpacing(6)

        # Save button
        self.btn_save = QPushButton("💾  Save MP3")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.setMinimumHeight(44)
        self.btn_save.setEnabled(False)
        layout.addWidget(self.btn_save)

        self.lbl_output_info = QLabel("")
        self.lbl_output_info.setObjectName("infoLabel")
        self.lbl_output_info.setWordWrap(True)
        layout.addWidget(self.lbl_output_info)

        layout.addStretch()
        return group

    def _build_progress_panel(self) -> QGroupBox:
        """Bottom progress panel."""
        group = QGroupBox("📊  Progress")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.lbl_status = QLabel("Ready")
        self.lbl_status.setObjectName("statusLabel")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        self.lbl_detail = QLabel("")
        self.lbl_detail.setObjectName("infoLabel")
        self.lbl_detail.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_detail)

        return group

    # ── Signal wiring ────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.btn_select_pdf.clicked.connect(self._on_select_pdf)
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_save.clicked.connect(self._on_save)

    # ── Slots ────────────────────────────────────────────────────

    @Slot()
    def _on_select_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF file",
            "",
            "PDF files (*.pdf);;All files (*.*)",
        )
        if path:
            self._pdf_path = path
            self.lbl_pdf_path.setText(Path(path).name)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.lbl_pdf_info.setText(f"Size: {size_mb:.1f} MB\nPath: {path}")
            self.btn_generate.setEnabled(True)
            self.btn_save.setEnabled(False)
            self.lbl_status.setText("PDF selected — ready to generate")
            self.progress_bar.setValue(0)

    @Slot()
    def _on_generate(self) -> None:
        if not self._pdf_path:
            return

        engine_idx = self.combo_engine.currentIndex()
        self.settings.tts.engine = "edge" if engine_idx == 0 else "sapi"

        if self.settings.tts.engine == "edge":
            # Extract voice ID from the label (everything before the first space)
            voice_label = self.combo_voice.currentText()
            self.settings.tts.voice = voice_label.split(" ")[0]
        else:
            self.settings.tts.voice = self.combo_voice.currentText()

        self._output_path = os.path.join(
            self.settings.temp_dir,
            Path(self._pdf_path).stem + "_audiobook.mp3",
        )

        # Lock UI while processing
        self.btn_generate.setEnabled(False)
        self.btn_select_pdf.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_cancel.setVisible(True)
        self.btn_save.setEnabled(False)
        self.combo_engine.setEnabled(False)
        self.combo_language.setEnabled(False)
        self.combo_voice.setEnabled(False)

        self.pipeline = AudioBookPipeline(self.settings)
        self.worker = PipelineWorker(self.pipeline, self._pdf_path, self._output_path)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    @Slot()
    def _on_cancel(self) -> None:
        if self.pipeline:
            self.pipeline.cancel()
        self.btn_cancel.setEnabled(False)
        self.lbl_status.setText("Cancelling...")

    @Slot()
    def _on_save(self) -> None:
        if not self._output_path or not os.path.exists(self._output_path):
            QMessageBox.warning(self, "Error", "No audio file available to save.")
            return

        default_name = (Path(self._pdf_path).stem + ".mp3") if self._pdf_path else "audiobook.mp3"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audiobook",
            default_name,
            "MP3 files (*.mp3);;All files (*.*)",
        )
        if save_path:
            import shutil
            shutil.copy2(self._output_path, save_path)
            self.lbl_output_info.setText(f"Saved to:\n{save_path}")
            QMessageBox.information(
                self,
                "Saved",
                f"Audiobook saved successfully:\n{save_path}",
            )

    @Slot(object)
    def _on_progress(self, progress: PipelineProgress) -> None:
        self.progress_bar.setValue(int(progress.progress * 1000))
        self.lbl_status.setText(progress.message)
        self.lbl_detail.setText(progress.detail)

    @Slot(object)
    def _on_finished(self, result: PipelineResult) -> None:
        # Restore UI
        self.btn_generate.setEnabled(True)
        self.btn_select_pdf.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setVisible(False)
        self.combo_engine.setEnabled(True)
        self.combo_language.setEnabled(True)
        self.combo_voice.setEnabled(True)

        if result.success:
            self.btn_save.setEnabled(True)
            self.lbl_status.setText("Audiobook generated successfully!")
            self.lbl_detail.setText(
                f"Processing time: {result.duration_secs:.0f}s · "
                f"{result.total_chunks} chunks · "
                f"{result.chapters_detected} chapters"
            )
            if result.output_path and os.path.exists(result.output_path):
                size_mb = os.path.getsize(result.output_path) / (1024 * 1024)
                self.lbl_output_info.setText(
                    f"File: {size_mb:.1f} MB\n"
                    f"Chunks: {result.total_chunks}\n"
                    f"Characters: {result.total_chars:,}"
                )
        else:
            self.lbl_status.setText(f"Error: {result.error}")
            self.progress_bar.setValue(0)
            if result.error and result.error != "Cancelled by user":
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred during generation:\n{result.error}",
                )

    # ── Helpers ──────────────────────────────────────────────────

    @Slot(int)
    def _on_engine_changed(self, index: int) -> None:
        """Show/hide language + voice controls based on selected engine."""
        is_edge = index == 0
        self.lbl_language.setVisible(is_edge)
        self.combo_language.setVisible(is_edge)
        self.lbl_voice.setVisible(is_edge)
        self.combo_voice.setVisible(is_edge)

        if not is_edge:
            self.combo_voice.clear()
            self.combo_voice.addItem("System Voice (SAPI5)")

    @Slot(int)
    def _on_language_changed(self, _index: int) -> None:
        """Filter the voice list when the language selection changes."""
        lang = self.combo_language.currentText()
        self._populate_voices(lang)

    def _populate_voices(self, language: str) -> None:
        """Fill the voice combo for the given language filter."""
        self.combo_voice.clear()
        if language == "All Languages":
            voices = _all_voices()
        else:
            voices = _VOICES_BY_LANG.get(language, [])

        for _voice_id, label in voices:
            self.combo_voice.addItem(label)
