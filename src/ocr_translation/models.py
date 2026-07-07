from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TextBlock:
    page_number: int
    order: tuple[float, float, int]
    text: str
    source: str


@dataclass(frozen=True)
class ExtractionResult:
    source_path: Path
    blocks: list[TextBlock]

    @property
    def plain_paragraphs(self) -> list[str]:
        return [block.text.strip() for block in self.blocks if block.text.strip()]
