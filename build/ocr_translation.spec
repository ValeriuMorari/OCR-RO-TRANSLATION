# Build this spec on Windows:
#   pyinstaller --clean --noconfirm build\ocr_translation.spec

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

block_cipher = None
project_root = Path(SPECPATH).resolve().parent
entry_script = project_root / "src" / "ocr_translation" / "main.py"

datas = []
binaries = []
hiddenimports = [
    "docx",
    "fitz",
    "PIL",
    "pytesseract",
    "sentencepiece",
    "torch",
    "transformers",
]


def require_tree(source: Path, target: str) -> None:
    if not source.exists():
        raise SystemExit(f"Required packaging asset is missing: {source}")
    datas.append((str(source), target))


def collect_package_metadata(package: str) -> None:
    try:
        datas.extend(copy_metadata(package))
    except Exception as exc:
        print(f"Warning: could not collect metadata for {package}: {exc}")


def collect_package_data(package: str) -> None:
    try:
        datas.extend(collect_data_files(package))
    except Exception as exc:
        print(f"Warning: could not collect data files for {package}: {exc}")


def collect_package_binaries(package: str) -> None:
    try:
        binaries.extend(collect_dynamic_libs(package))
    except Exception as exc:
        print(f"Warning: could not collect dynamic libraries for {package}: {exc}")


require_tree(project_root / "assets" / "models" / "opus-mt-en-ro", "assets/models/opus-mt-en-ro")
require_tree(project_root / "assets" / "tesseract", "assets/tesseract")

for package_name in [
    "filelock",
    "huggingface_hub",
    "numpy",
    "packaging",
    "pymupdf",
    "regex",
    "requests",
    "safetensors",
    "sentencepiece",
    "tokenizers",
    "torch",
    "tqdm",
    "transformers",
    "typing_extensions",
]:
    collect_package_metadata(package_name)

for package_name in [
    "certifi",
    "charset_normalizer",
    "huggingface_hub",
    "safetensors",
    "sentencepiece",
    "tokenizers",
    "torch",
    "transformers",
]:
    collect_package_data(package_name)

for package_name in ["torch", "tokenizers", "sentencepiece"]:
    collect_package_binaries(package_name)

hiddenimports.extend(collect_submodules("transformers"))
hiddenimports.extend(collect_submodules("torch"))

a = Analysis(
    [str(entry_script)],
    pathex=[str(project_root), str(project_root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OCRTranslation",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="OCRTranslation",
)
