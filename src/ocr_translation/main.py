from __future__ import annotations

import sys
from pathlib import Path

from ocr_translation.errors import AppError
from ocr_translation.processor import output_paths as _output_paths
from ocr_translation.processor import process_document


def main() -> int:
    print("OCR Translation Console")
    print("Paste a PDF or DOCX path. Command-line arguments are not used.")

    try:
        input_path = _read_input_path()
        result = process_document(input_path, progress=print)

        print("Done.")
        print(f"English output: {result.english_path}")
        print(f"Romanian output: {result.romanian_path}")
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


if __name__ == "__main__":
    sys.exit(main())
