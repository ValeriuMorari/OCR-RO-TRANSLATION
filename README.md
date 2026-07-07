# OCR Translation Console App

Python console application for Windows that asks for a `.pdf` or `.docx` path, extracts English text, uses OCR for image/scanned content, translates the text to Romanian, and writes two text-only Word documents.

## Outputs

For an input such as `book.pdf`, the app writes:

- `book_extracted_en.docx`
- `book_translated_ro.docx`

## Development Run

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\download_model.py
python scripts\check_environment.py
python -m ocr_translation.main
```

The app does not use command-line arguments. Paste the document path when prompted.

## OCR Requirement

Tesseract OCR is required for scanned pages or text inside images. For development, install Tesseract for Windows and make sure `tesseract.exe` is on `PATH`, or set:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

On macOS development machines, install the native executable with:

```bash
brew install tesseract
python scripts/check_environment.py
```

For a packaged Windows build, place Tesseract binaries under `assets\tesseract\` and English trained data under `assets\tesseract\tessdata\eng.traineddata`.

## Offline Translation Model

The setup script downloads `Helsinki-NLP/opus-mt-en-ro` into:

```text
assets/models/opus-mt-en-ro
```

Normal app runs then use that local folder.

## Build Windows EXE

Build on Windows 64-bit. The final deliverable for users should be the Inno Setup installer:

```text
Output\OCRTranslationSetup.exe
```

The user does not need Python, Tesseract, or the Hugging Face model installed separately.

### 1. Prepare bundled Tesseract

Place a portable Windows Tesseract distribution here:

```text
assets\tesseract\
  tesseract.exe
  *.dll
  tessdata\eng.traineddata
```

You can also let the build script copy an existing Tesseract install into `assets\tesseract` by passing `-TesseractSource`.
If Tesseract is installed at `C:\Program Files\Tesseract-OCR`, the build script uses that folder automatically.

### 2. Build the PyInstaller folder

```powershell
.\scripts\build_windows.ps1 -TesseractSource "C:\Program Files\Tesseract-OCR"
```

Or, when Tesseract is already installed in the default folder:

```powershell
.\scripts\build_windows.ps1
```

The script installs Python dependencies into `.venv`, downloads the translation model, validates assets, and builds:

```text
dist\OCRTranslation\OCRTranslation.exe
```

### 3. Build the installer

If Inno Setup is installed and `iscc` is on `PATH`, the build script also creates:

```text
Output\OCRTranslationSetup.exe
```

Otherwise install Inno Setup and run:

```powershell
iscc build\installer.iss
```

### Manual build commands

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\download_model.py
python scripts\validate_package.py
pyinstaller --clean --noconfirm build\ocr_translation.spec
python scripts\validate_package.py --dist dist\OCRTranslation
iscc build\installer.iss
```

## Build With GitHub Actions

Push this repository to GitHub, then open:

```text
Actions -> Build Windows Installer -> Run workflow
```

The workflow builds on a Windows runner, installs Tesseract and Inno Setup, downloads the translation model, packages the app, and uploads this artifact:

```text
OCRTranslationSetup.exe
```

That installer is the file to share with Windows users. They do not need Python, Tesseract, or the Hugging Face model installed separately.

## Notes

- PDFs with selectable text are extracted directly.
- PDF image blocks are OCRed in page-coordinate order so mixed text and image text stays understandable.
- Pages with little or no selectable text are OCRed as full-page images.
- DOCX paragraphs and tables are read in document order; inline images are OCRed near their paragraph position.
