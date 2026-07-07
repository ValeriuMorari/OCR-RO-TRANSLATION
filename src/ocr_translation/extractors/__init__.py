from pathlib import Path

from ocr_translation.errors import UnsupportedFileError
from ocr_translation.extractors.docx_extractor import DocxExtractor
from ocr_translation.extractors.pdf_extractor import PdfExtractor
from ocr_translation.models import ExtractionResult
from ocr_translation.ocr import TesseractOcrEngine


def extract_document(path: Path, ocr_engine: TesseractOcrEngine) -> ExtractionResult:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PdfExtractor(ocr_engine=ocr_engine).extract(path)
    if suffix == ".docx":
        return DocxExtractor(ocr_engine=ocr_engine).extract(path)
    raise UnsupportedFileError("Only .pdf and .docx files are supported.")
