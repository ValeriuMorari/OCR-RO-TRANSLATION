param(
    [string]$PythonCommand = "py -3.12",
    [string]$TesseractSource = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Project root: $ProjectRoot"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment with $PythonCommand"
    Invoke-Expression "$PythonCommand -m venv .venv"
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvPip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"
$PyInstaller = Join-Path $ProjectRoot ".venv\Scripts\pyinstaller.exe"

& $VenvPython -m pip install --upgrade pip
& $VenvPip install -r requirements.txt
& $VenvPython scripts\download_model.py

if ($TesseractSource -eq "" -and (Test-Path "C:\Program Files\Tesseract-OCR")) {
    $TesseractSource = "C:\Program Files\Tesseract-OCR"
}

if ($TesseractSource -ne "") {
    if (-not (Test-Path $TesseractSource)) {
        throw "TesseractSource does not exist: $TesseractSource"
    }

    $Target = Join-Path $ProjectRoot "assets\tesseract"
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Write-Host "Copying Tesseract from $TesseractSource to $Target"
    Copy-Item -Path (Join-Path $TesseractSource "*") -Destination $Target -Recurse -Force
}

& $VenvPython scripts\validate_package.py
& $PyInstaller --clean --noconfirm build\ocr_translation.spec
& $VenvPython scripts\validate_package.py --dist dist\OCRTranslation

$IsccCommand = Get-Command iscc -ErrorAction SilentlyContinue
$IsccPath = if ($IsccCommand) { $IsccCommand.Source } else { "" }
if ($IsccPath -eq "" -and (Test-Path "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe")) {
    $IsccPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
}
if ($IsccPath -eq "" -and (Test-Path "$env:ProgramFiles\Inno Setup 6\ISCC.exe")) {
    $IsccPath = "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
}

if ($IsccPath -ne "") {
    & $IsccPath build\installer.iss
    Write-Host "Installer created under Output\OCRTranslationSetup.exe"
} else {
    Write-Host "Inno Setup compiler 'iscc' was not found on PATH."
    Write-Host "Install Inno Setup, then run: iscc build\installer.iss"
}

Write-Host "Build output: dist\OCRTranslation\OCRTranslation.exe"
