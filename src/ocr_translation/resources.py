from __future__ import annotations

import os
import sys
from pathlib import Path


def app_root() -> Path:
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        return Path(bundled_root)
    return _first_existing_root("assets") or Path.cwd()


def bundled_path(*parts: str) -> Path:
    relative = Path(*parts)
    root = _first_existing_root(str(relative.parts[0])) if relative.parts else None
    return (root or app_root()).joinpath(relative)


def default_model_path() -> Path:
    configured = os.environ.get("TRANSLATION_MODEL_DIR")
    if configured:
        return Path(configured)
    return bundled_path("assets", "models", "opus-mt-en-ro")


def default_tesseract_cmd() -> str | None:
    configured = os.environ.get("TESSERACT_CMD")
    if configured:
        return configured

    exe_name = "tesseract.exe" if os.name == "nt" else "tesseract"
    candidate = bundled_path("assets", "tesseract", exe_name)
    if candidate.exists():
        return str(candidate)
    return None


def default_tessdata_prefix() -> str | None:
    configured = os.environ.get("TESSDATA_PREFIX")
    if configured:
        return configured

    candidate = bundled_path("assets", "tesseract", "tessdata")
    if candidate.exists():
        return str(candidate)
    return None


def _first_existing_root(required_child: str) -> Path | None:
    package_file = Path(__file__).resolve()
    candidates = [
        Path.cwd(),
        *Path.cwd().parents,
        package_file.parents[2],
        *package_file.parents,
    ]

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / required_child).exists():
            return candidate
    return None
