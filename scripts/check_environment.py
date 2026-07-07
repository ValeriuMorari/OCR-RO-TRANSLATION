from __future__ import annotations

import importlib.util
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "assets" / "models" / "opus-mt-en-ro"


def main() -> int:
    checks = [
        ("pymupdf / fitz", _module_ok("fitz"), "pip install -r requirements.txt"),
        ("python-docx / docx", _module_ok("docx"), "pip install -r requirements.txt"),
        ("Pillow / PIL", _module_ok("PIL"), "pip install -r requirements.txt"),
        ("pytesseract", _module_ok("pytesseract"), "pip install -r requirements.txt"),
        ("transformers", _module_ok("transformers"), "pip install -r requirements.txt"),
        ("torch", _module_ok("torch"), "pip install -r requirements.txt"),
        ("sentencepiece", _module_ok("sentencepiece"), "pip install -r requirements.txt"),
        ("Tesseract executable", _tesseract_ok(), _tesseract_hint()),
        ("English-to-Romanian model", MODEL_DIR.exists(), "python scripts/download_model.py"),
    ]

    failed = False
    for label, ok, hint in checks:
        status = "OK" if ok else "MISSING"
        print(f"{status:8} {label}")
        if not ok:
            failed = True
            print(f"         {hint}")

    return 1 if failed else 0


def _module_ok(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _tesseract_ok() -> bool:
    configured = os.environ.get("TESSERACT_CMD")
    if configured and Path(configured).exists():
        return True
    return shutil.which("tesseract") is not None


def _tesseract_hint() -> str:
    if os.name == "nt":
        return (
            "Install Tesseract OCR, then set: "
            '$env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"'
        )
    return "Install with: brew install tesseract"


if __name__ == "__main__":
    raise SystemExit(main())
