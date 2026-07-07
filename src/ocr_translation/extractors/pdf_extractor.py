from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

from ocr_translation.errors import DependencyMissingError
from ocr_translation.models import ExtractionResult, TextBlock
from ocr_translation.ocr import TesseractOcrEngine


@dataclass
class PdfExtractor:
    ocr_engine: TesseractOcrEngine
    full_page_ocr_threshold_chars: int = 25
    render_dpi: int = 220

    def extract(self, path: Path) -> ExtractionResult:
        try:
            import fitz
        except ImportError as exc:
            raise DependencyMissingError(
                "PyMuPDF is not installed. Install requirements.txt before reading PDFs."
            ) from exc

        blocks: list[TextBlock] = []
        with fitz.open(path) as document:
            for page_index, page in enumerate(document):
                page_number = page_index + 1
                page_blocks = self._extract_page_blocks(page, page_number)
                if self._native_text_length(page_blocks) < self.full_page_ocr_threshold_chars:
                    full_page_text = self._ocr_full_page(page, fitz)
                    if full_page_text:
                        page_blocks = [
                            TextBlock(
                                page_number=page_number,
                                order=(0.0, 0.0, 0),
                                text=full_page_text,
                                source="ocr-page",
                            )
                        ]
                blocks.extend(sorted(page_blocks, key=lambda block: block.order))

        return ExtractionResult(source_path=path, blocks=blocks)

    def _extract_page_blocks(self, page: object, page_number: int) -> list[TextBlock]:
        raw = page.get_text("dict", sort=True)
        blocks: list[TextBlock] = []
        for index, block in enumerate(raw.get("blocks", [])):
            bbox = block.get("bbox", (0.0, 0.0, 0.0, 0.0))
            order = (float(bbox[1]), float(bbox[0]), index)

            if block.get("type") == 0:
                text = self._text_from_block(block)
                if text:
                    blocks.append(TextBlock(page_number, order, text, "pdf-text"))
            elif block.get("type") == 1:
                text = self._ocr_image_block(block)
                if text:
                    blocks.append(TextBlock(page_number, order, text, "ocr-image"))

        return blocks

    def _text_from_block(self, block: dict) -> str:
        lines: list[str] = []
        for line in block.get("lines", []):
            spans = [span.get("text", "") for span in line.get("spans", [])]
            line_text = " ".join("".join(spans).split())
            if line_text:
                lines.append(line_text)
        return "\n".join(lines).strip()

    def _ocr_image_block(self, block: dict) -> str:
        image_bytes = block.get("image")
        if not image_bytes:
            return ""
        try:
            return self.ocr_engine.image_bytes_to_text(image_bytes)
        except Exception:
            return ""

    def _ocr_full_page(self, page: object, fitz_module: object) -> str:
        zoom = self.render_dpi / 72.0
        matrix = fitz_module.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image_bytes = pixmap.tobytes("png")
        return self.ocr_engine.image_bytes_to_text(image_bytes)

    def _native_text_length(self, blocks: list[TextBlock]) -> int:
        return sum(len(block.text) for block in blocks if block.source == "pdf-text")
