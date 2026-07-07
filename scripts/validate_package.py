from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_MODEL_FILES = [
    "config.json",
    "generation_config.json",
    "pytorch_model.bin",
    "source.spm",
    "target.spm",
    "tokenizer_config.json",
    "vocab.json",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Windows packaging assets or PyInstaller output.")
    parser.add_argument(
        "--dist",
        type=Path,
        default=None,
        help="Optional dist/OCRTranslation folder to validate after PyInstaller.",
    )
    args = parser.parse_args()

    root = args.dist or Path.cwd()
    asset_root = _resolve_asset_root(root)
    checks = _asset_checks(asset_root)
    if args.dist is not None:
        checks.insert(0, (root / "OCRTranslation.exe", "PyInstaller executable"))

    failed = False
    for path, label in checks:
        ok = path.exists()
        print(f"{'OK':8} {label}: {path}" if ok else f"{'MISSING':8} {label}: {path}")
        failed = failed or not ok

    if failed:
        print("")
        print("Packaging validation failed. Add the missing files before building or shipping.")
        return 1
    return 0


def _resolve_asset_root(root: Path) -> Path:
    if (root / "assets").exists():
        return root
    if (root / "_internal" / "assets").exists():
        return root / "_internal"
    return root


def _asset_checks(root: Path) -> list[tuple[Path, str]]:
    tesseract_exe = "tesseract.exe"
    checks: list[tuple[Path, str]] = [
        (root / "assets" / "tesseract" / tesseract_exe, "Tesseract executable"),
        (root / "assets" / "tesseract" / "tessdata" / "eng.traineddata", "English OCR data"),
    ]
    for file_name in REQUIRED_MODEL_FILES:
        checks.append(
            (
                root / "assets" / "models" / "opus-mt-en-ro" / file_name,
                f"Translation model file {file_name}",
            )
        )
    return checks


if __name__ == "__main__":
    raise SystemExit(main())
