from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

from ocr_translation.errors import DependencyMissingError
from ocr_translation.models import ExtractionResult, TextBlock
from ocr_translation.ocr import TesseractOcrEngine


@dataclass
class DocxExtractor:
    ocr_engine: TesseractOcrEngine

    def extract(self, path: Path) -> ExtractionResult:
        try:
            from docx import Document
            from docx.table import Table
            from docx.text.paragraph import Paragraph
        except ImportError as exc:
            raise DependencyMissingError(
                "python-docx is not installed. Install requirements.txt before reading DOCX files."
            ) from exc

        document = Document(path)
        blocks: list[TextBlock] = []
        order_index = 0

        for child in document.element.body.iterchildren():
            if child.tag.endswith("}p"):
                paragraph = Paragraph(child, document)
                order_index = self._append_paragraph_blocks(blocks, paragraph, order_index)
            elif child.tag.endswith("}tbl"):
                table = Table(child, document)
                order_index = self._append_table_blocks(blocks, table, order_index)

        return ExtractionResult(source_path=path, blocks=blocks)

    def _append_paragraph_blocks(
        self,
        blocks: list[TextBlock],
        paragraph: object,
        order_index: int,
    ) -> int:
        text = " ".join(paragraph.text.split())
        if text:
            blocks.append(TextBlock(1, (float(order_index), 0.0, order_index), text, "docx-text"))
            order_index += 1

        for image_bytes in self._paragraph_image_bytes(paragraph):
            ocr_text = self.ocr_engine.image_bytes_to_text(image_bytes)
            if ocr_text:
                blocks.append(TextBlock(1, (float(order_index), 0.0, order_index), ocr_text, "ocr-image"))
                order_index += 1
        return order_index

    def _append_table_blocks(self, blocks: list[TextBlock], table: object, order_index: int) -> int:
        for row in table.rows:
            row_text = " | ".join(" ".join(cell.text.split()) for cell in row.cells if cell.text.strip())
            if row_text:
                blocks.append(TextBlock(1, (float(order_index), 0.0, order_index), row_text, "docx-table"))
                order_index += 1

            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for image_bytes in self._paragraph_image_bytes(paragraph):
                        ocr_text = self.ocr_engine.image_bytes_to_text(image_bytes)
                        if ocr_text:
                            blocks.append(
                                TextBlock(1, (float(order_index), 0.0, order_index), ocr_text, "ocr-image")
                            )
                            order_index += 1
        return order_index

    def _paragraph_image_bytes(self, paragraph: object) -> list[bytes]:
        images: list[bytes] = []
        relationship_ids = paragraph._element.xpath(".//a:blip/@r:embed")
        for relationship_id in relationship_ids:
            part = paragraph.part.related_parts.get(relationship_id)
            if part is not None:
                images.append(part.blob)
        return images
