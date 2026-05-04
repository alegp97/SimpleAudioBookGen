"""
Extracción de texto desde PDF.

Usa PyMuPDF para PDFs con texto y pytesseract como fallback para PDFs escaneados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from audiobook_gen.utils.logger import get_logger

log = get_logger("pdf_extractor")


@dataclass
class PageContent:
    """Contenido de una página del PDF."""
    page_number: int
    text: str
    is_ocr: bool = False


@dataclass
class PDFMetadata:
    """Metadatos del PDF."""
    title: Optional[str] = None
    author: Optional[str] = None
    total_pages: int = 0
    is_scanned: bool = False


@dataclass
class ExtractionResult:
    """Resultado completo de la extracción."""
    metadata: PDFMetadata = field(default_factory=PDFMetadata)
    pages: list[PageContent] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.text for p in self.pages if p.text.strip())


class PDFExtractor:
    """Extrae texto de archivos PDF, con fallback OCR."""

    # Si el ratio promedio de caracteres por página es menor que esto,
    # se considera un PDF escaneado
    SCANNED_THRESHOLD = 50

    def extract(self, pdf_path: str | Path) -> ExtractionResult:
        """
        Extrae texto de un PDF.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            ExtractionResult con páginas y metadatos.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el archivo no es un PDF válido.
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"El archivo no es un PDF: {pdf_path}")

        log.info("Abriendo PDF: %s", pdf_path.name)

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            raise ValueError(f"No se pudo abrir el PDF: {e}") from e

        metadata = PDFMetadata(
            title=doc.metadata.get("title") or None,
            author=doc.metadata.get("author") or None,
            total_pages=len(doc),
        )

        log.info(
            "PDF abierto — Páginas: %d, Título: %s, Autor: %s",
            metadata.total_pages,
            metadata.title or "(sin título)",
            metadata.author or "(sin autor)",
        )

        # Primer paso: intentar extracción directa de texto
        pages = self._extract_text(doc)

        # Evaluar si el PDF es escaneado
        avg_chars = (
            sum(len(p.text) for p in pages) / max(len(pages), 1)
        )
        if avg_chars < self.SCANNED_THRESHOLD:
            log.warning(
                "PDF parece escaneado (promedio %.0f chars/página). Intentando OCR...",
                avg_chars,
            )
            metadata.is_scanned = True
            pages = self._extract_with_ocr(doc)

        doc.close()

        result = ExtractionResult(metadata=metadata, pages=pages)
        total_chars = sum(len(p.text) for p in pages)
        log.info(
            "Extracción completada — %d páginas, %d caracteres totales",
            len(result.pages),
            total_chars,
        )

        return result

    def _extract_text(self, doc: fitz.Document) -> list[PageContent]:
        """Extrae texto directamente con PyMuPDF."""
        pages: list[PageContent] = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append(PageContent(page_number=i + 1, text=text))
        return pages

    def _extract_with_ocr(self, doc: fitz.Document) -> list[PageContent]:
        """Extrae texto usando OCR (pytesseract)."""
        try:
            import pytesseract
            from PIL import Image
            import io
            import sys
            import os
            
            # Configure Tesseract path if running as bundled app
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
                tesseract_exe = base_path / "tesseract_bin" / "tesseract.exe"
                if tesseract_exe.exists():
                    pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
                    log.debug("Using bundled Tesseract at %s", tesseract_exe)
                
        except ImportError:
            log.error(
                "pytesseract o Pillow no están instalados. "
                "Instala: pip install pytesseract Pillow"
            )
            return []

        pages: list[PageContent] = []
        for i, page in enumerate(doc):
            # Renderizar página como imagen
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))

            try:
                text = pytesseract.image_to_string(image, lang="spa")
            except Exception as e:
                log.warning("OCR falló en página %d: %s", i + 1, e)
                text = ""

            pages.append(PageContent(page_number=i + 1, text=text, is_ocr=True))
            log.debug("OCR página %d: %d caracteres", i + 1, len(text))

        return pages
