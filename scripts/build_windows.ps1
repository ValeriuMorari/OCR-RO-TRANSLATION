param(
    [string]$PythonCommand = "py -3.12",
    [string]$TesseractSource = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Project root: $ProjectRoot"

function Assert-LastExitCode {
    param([string]$StepName)

    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE"
    }
}

function Invoke-CheckedExpression {
    param(
        [string]$Command,
        [string]$StepName
    )

    Invoke-Expression $Command
    Assert-LastExitCode $StepName
}

function Invoke-CheckedCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$StepName
    )

    & $FilePath @Arguments
    Assert-LastExitCode $StepName
}

function Find-TesseractSource {
    $candidateRoots = @()

    if ($TesseractSource -ne "") {
        $candidateRoots += $TesseractSource
    }

    $command = Get-Command tesseract -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        $candidateRoots += (Split-Path $command.Source -Parent)
    }

    $knownRoots = @(
        "C:\Program Files\Tesseract-OCR",
        "C:\Program Files (x86)\Tesseract-OCR",
        "$env:ChocolateyInstall\lib\tesseract",
        "C:\ProgramData\chocolatey\lib\tesseract"
    )

    foreach ($root in $knownRoots) {
        if ($root -and (Test-Path $root)) {
            $candidateRoots += $root
        }
    }

    foreach ($root in ($candidateRoots | Select-Object -Unique)) {
        if (-not (Test-Path $root)) {
            continue
        }

        $directExe = Join-Path $root "tesseract.exe"
        if ((Test-Path $directExe) -and (Test-Path (Join-Path $root "tessdata\eng.traineddata"))) {
            return $root
        }

        $exe = Get-ChildItem -Path $root -Filter "tesseract.exe" -Recurse -ErrorAction SilentlyContinue |
            Where-Object { Test-Path (Join-Path $_.DirectoryName "tessdata\eng.traineddata") } |
            Select-Object -First 1

        if ($exe) {
            return $exe.DirectoryName
        }
    }

    Write-Host "Could not locate a complete Tesseract folder."
    Write-Host "Expected a folder containing tesseract.exe and tessdata\eng.traineddata."
    Write-Host "Checked roots:"
    foreach ($root in ($candidateRoots | Select-Object -Unique)) {
        Write-Host "  $root"
    }
    return ""
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment with $PythonCommand"
    Invoke-CheckedExpression "$PythonCommand -m venv .venv" "Create virtual environment"
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvPip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"
$PyInstaller = Join-Path $ProjectRoot ".venv\Scripts\pyinstaller.exe"

Invoke-CheckedCommand $VenvPython @("-m", "pip", "install", "--upgrade", "pip") "Upgrade pip"
Invoke-CheckedCommand $VenvPip @("install", "-r", "requirements.txt") "Install Python requirements"
Invoke-CheckedCommand $VenvPython @("scripts\download_model.py") "Download translation model"

$ResolvedTesseractSource = Find-TesseractSource
if ($ResolvedTesseractSource -ne "") {
    $Target = Join-Path $ProjectRoot "assets\tesseract"
    if (Test-Path $Target) {
        Remove-Item -Path $Target -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Write-Host "Copying Tesseract from $ResolvedTesseractSource to $Target"
    Copy-Item -Path (Join-Path $ResolvedTesseractSource "*") -Destination $Target -Recurse -Force
}

Invoke-CheckedCommand $VenvPython @("scripts\validate_package.py") "Validate source packaging assets"
Invoke-CheckedCommand $PyInstaller @("--clean", "--noconfirm", "build\ocr_translation.spec") "Build PyInstaller package"
Invoke-CheckedCommand $VenvPython @("scripts\validate_package.py", "--dist", "dist\OCRTranslation") "Validate PyInstaller output"

$IsccCommand = Get-Command iscc -ErrorAction SilentlyContinue
$IsccPath = if ($IsccCommand) { $IsccCommand.Source } else { "" }
if ($IsccPath -eq "" -and (Test-Path "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe")) {
    $IsccPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
}
if ($IsccPath -eq "" -and (Test-Path "$env:ProgramFiles\Inno Setup 6\ISCC.exe")) {
    $IsccPath = "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
}

if ($IsccPath -ne "") {
    Invoke-CheckedCommand $IsccPath @("build\installer.iss") "Compile Inno Setup installer"
    Write-Host "Installer created under Output\OCRTranslationSetup.exe"
} else {
    throw "Inno Setup compiler 'iscc' was not found. Install Inno Setup, then run: iscc build\installer.iss"
}

Write-Host "Build output: dist\OCRTranslation\OCRTranslation.exe"
