from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ocr_translation.errors import DependencyMissingError
from ocr_translation.resources import default_model_path


@dataclass
class RomanianTranslator:
    model_path: Path | None = None
    max_input_tokens: int = 420
    max_output_tokens: int = 512

    def __post_init__(self) -> None:
        self.model_path = self.model_path or default_model_path()
        if not self.model_path.exists():
            raise DependencyMissingError(
                f"Translation model not found at {self.model_path}. Run scripts/download_model.py "
                "or set TRANSLATION_MODEL_DIR to a local Hugging Face model folder."
            )

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise DependencyMissingError(
                "transformers is not installed. Install requirements.txt before translating."
            ) from exc

        self._tokenizer = AutoTokenizer.from_pretrained(str(self.model_path), local_files_only=True)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(str(self.model_path), local_files_only=True)
        self._torch = _optional_torch()

    def translate_paragraphs(self, paragraphs: list[str]) -> list[str]:
        translated: list[str] = []
        for paragraph in paragraphs:
            chunks = self._split_for_model(paragraph)
            translated_chunks = [self._translate_chunk(chunk) for chunk in chunks if chunk.strip()]
            translated.append(" ".join(translated_chunks).strip())
        return translated

    def _translate_chunk(self, text: str) -> str:
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=self.max_input_tokens)
        with _no_grad(self._torch):
            output_tokens = self._model.generate(
                **inputs,
                max_length=self.max_output_tokens,
                num_beams=4,
                early_stopping=True,
            )
        return self._tokenizer.decode(output_tokens[0], skip_special_tokens=True).strip()

    def _split_for_model(self, text: str) -> list[str]:
        sentences = _sentence_split(text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if not current or self._token_count(candidate) <= self.max_input_tokens:
                current = candidate
                continue

            chunks.extend(self._force_split_if_needed(current))
            current = sentence

        if current:
            chunks.extend(self._force_split_if_needed(current))
        return chunks

    def _force_split_if_needed(self, text: str) -> list[str]:
        if self._token_count(text) <= self.max_input_tokens:
            return [text]

        words = text.split()
        chunks: list[str] = []
        current_words: list[str] = []
        for word in words:
            candidate = " ".join([*current_words, word])
            if current_words and self._token_count(candidate) > self.max_input_tokens:
                chunks.append(" ".join(current_words))
                current_words = [word]
            else:
                current_words.append(word)
        if current_words:
            chunks.append(" ".join(current_words))
        return chunks

    def _token_count(self, text: str) -> int:
        return len(self._tokenizer(text, add_special_tokens=True).input_ids)


def _sentence_split(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _optional_torch() -> object | None:
    try:
        import torch
    except ImportError:
        return None
    return torch


class _NoOpContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        return False


def _no_grad(torch_module: object | None) -> object:
    if torch_module is None:
        return _NoOpContext()
    return torch_module.no_grad()
