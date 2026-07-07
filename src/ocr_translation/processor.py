from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ocr_translation.errors import AppError
from ocr_translation.export import DocxWriter
from ocr_translation.extractors import extract_document
from ocr_translation.ocr import TesseractOcrEngine
from ocr_translation.translation import RomanianTranslator


ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class ProcessingResult:
    english_path: Path
    romanian_path: Path


def process_document(input_path: Path, progress: ProgressCallback | None = None) -> ProcessingResult:
    _validate_input_path(input_path)
    english_path, romanian_path = output_paths(input_path)

    _notify(progress, "Loading OCR engine...")
    ocr_engine = TesseractOcrEngine(language="eng")

    _notify(progress, f"Extracting English text from: {input_path}")
    extraction = extract_document(input_path, ocr_engine)
    if not extraction.blocks:
        raise AppError("No text was extracted from the document.")

    _notify(progress, f"Writing English DOCX: {english_path}")
    DocxWriter(title="Extracted English Text").write_blocks(english_path, extraction.blocks)

    _notify(progress, "Loading offline English-to-Romanian translation model...")
    translator = RomanianTranslator()

    paragraphs = extraction.plain_paragraphs
    _notify(progress, f"Translating {len(paragraphs)} text blocks to Romanian...")
    translated_paragraphs = translator.translate_paragraphs(paragraphs)

    _notify(progress, f"Writing Romanian DOCX: {romanian_path}")
    DocxWriter(title="Romanian Translation").write_paragraphs(romanian_path, translated_paragraphs)

    return ProcessingResult(english_path=english_path, romanian_path=romanian_path)


def output_paths(input_path: Path) -> tuple[Path, Path]:
    stem = input_path.with_suffix("")
    return (
        stem.with_name(f"{stem.name}_extracted_en.docx"),
        stem.with_name(f"{stem.name}_translated_ro.docx"),
    )


def _validate_input_path(path: Path) -> None:
    if not path.exists():
        raise AppError(f"File does not exist: {path}")
    if not path.is_file():
        raise AppError(f"Path is not a file: {path}")
    if path.suffix.lower() not in {".pdf", ".docx"}:
        raise AppError("Only .pdf and .docx files are supported.")


def _notify(progress: ProgressCallback | None, message: str) -> None:
    if progress:
        progress(message)
