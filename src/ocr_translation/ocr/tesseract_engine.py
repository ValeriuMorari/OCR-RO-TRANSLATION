from __future__ import annotations

import io
import os
import shutil
from dataclasses import dataclass

from ocr_translation.errors import DependencyMissingError
from ocr_translation.resources import default_tessdata_prefix, default_tesseract_cmd


@dataclass
class TesseractOcrEngine:
    language: str = "eng"
    min_confidence_text_chars: int = 2

    def __post_init__(self) -> None:
        try:
            import pytesseract
        except ImportError as exc:
            raise DependencyMissingError(
                "pytesseract is not installed. Install requirements.txt before using OCR."
            ) from exc

        configured_cmd = default_tesseract_cmd()
        if configured_cmd:
            pytesseract.pytesseract.tesseract_cmd = configured_cmd

        tessdata_prefix = default_tessdata_prefix()
        if tessdata_prefix:
            os.environ.setdefault("TESSDATA_PREFIX", tessdata_prefix)

        self._pytesseract = pytesseract

    def is_available(self) -> bool:
        configured_cmd = getattr(self._pytesseract.pytesseract, "tesseract_cmd", None)
        if configured_cmd and shutil.which(configured_cmd):
            return True
        if configured_cmd and os.path.exists(configured_cmd):
            return True
        return shutil.which("tesseract") is not None

    def image_bytes_to_text(self, image_bytes: bytes) -> str:
        try:
            from PIL import Image, ImageOps
        except ImportError as exc:
            raise DependencyMissingError(
                "Pillow is not installed. Install requirements.txt before using OCR."
            ) from exc

        with Image.open(io.BytesIO(image_bytes)) as image:
            return self.image_to_text(image)

    def image_to_text(self, image: object) -> str:
        processed = self._preprocess_image(image)
        try:
            text = self._pytesseract.image_to_string(processed, lang=self.language)
        except self._pytesseract.TesseractNotFoundError as exc:
            raise DependencyMissingError(
                "Tesseract OCR executable was not found.\n"
                "macOS development install: brew install tesseract\n"
                "Windows development install: install Tesseract OCR and set "
                'TESSERACT_CMD to C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n'
                "Packaged Windows build: bundle assets/tesseract/tesseract.exe and "
                "assets/tesseract/tessdata/eng.traineddata."
            ) from exc
        return self._clean_text(text)

    def _preprocess_image(self, image: object) -> object:
        from PIL import ImageOps

        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")
        grayscale = ImageOps.grayscale(image)
        return ImageOps.autocontrast(grayscale)

    def _clean_text(self, text: str) -> str:
        lines = [" ".join(line.split()) for line in text.splitlines()]
        non_empty = [line for line in lines if len(line) >= self.min_confidence_text_chars]
        return "\n".join(non_empty).strip()
