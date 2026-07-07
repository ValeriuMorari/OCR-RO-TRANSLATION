from __future__ import annotations

import sys
from pathlib import Path

from ocr_translation.errors import AppError
from ocr_translation.export import DocxWriter
from ocr_translation.extractors import extract_document
from ocr_translation.ocr import TesseractOcrEngine
from ocr_translation.translation import RomanianTranslator


def main() -> int:
    print("OCR Translation Console")
    print("Paste a PDF or DOCX path. Command-line arguments are not used.")

    try:
        input_path = _read_input_path()
        english_path, romanian_path = _output_paths(input_path)

        print("Loading OCR engine...")
        ocr_engine = TesseractOcrEngine(language="eng")

        print(f"Extracting English text from: {input_path}")
        extraction = extract_document(input_path, ocr_engine)
        if not extraction.blocks:
            raise AppError("No text was extracted from the document.")

        print(f"Writing English DOCX: {english_path}")
        DocxWriter(title="Extracted English Text").write_blocks(english_path, extraction.blocks)

        print("Loading offline English-to-Romanian translation model...")
        translator = RomanianTranslator()

        paragraphs = extraction.plain_paragraphs
        print(f"Translating {len(paragraphs)} text blocks to Romanian...")
        translated_paragraphs = translator.translate_paragraphs(paragraphs)

        print(f"Writing Romanian DOCX: {romanian_path}")
        DocxWriter(title="Romanian Translation").write_paragraphs(romanian_path, translated_paragraphs)

        print("Done.")
        print(f"English output: {english_path}")
        print(f"Romanian output: {romanian_path}")
        return 0
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    except AppError as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return 1


def _read_input_path() -> Path:
    raw_path = input("Document path: ").strip().strip('"')
    if not raw_path:
        raise AppError("No path was provided.")

    path = Path(raw_path).expanduser()
    if not path.exists():
        raise AppError(f"File does not exist: {path}")
    if not path.is_file():
        raise AppError(f"Path is not a file: {path}")
    if path.suffix.lower() not in {".pdf", ".docx"}:
        raise AppError("Only .pdf and .docx files are supported.")
    return path


def _output_paths(input_path: Path) -> tuple[Path, Path]:
    stem = input_path.with_suffix("")
    return (
        stem.with_name(f"{stem.name}_extracted_en.docx"),
        stem.with_name(f"{stem.name}_translated_ro.docx"),
    )


if __name__ == "__main__":
    sys.exit(main())
