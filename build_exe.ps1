# Builds a standalone Windows .exe with PyInstaller
# Usage: Run this script in PowerShell from the repo root

$ErrorActionPreference = 'Stop'

# Ensure we're at the script location (repo root)
Set-Location -Path $PSScriptRoot

# Create a clean dist/build
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }

# Install deps into current environment
if (Test-Path .\venv\Scripts\python.exe) {
    $python = (Resolve-Path .\venv\Scripts\python.exe).Path
} elseif (Test-Path .\.venv\Scripts\python.exe) {
    $python = (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    $python = 'python'
}

Write-Host "Using Python: $python"

# Pin installs if needed
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

# Collect data files (top-level images/fonts + assets and audio folders)
# PyInstaller --add-data needs src;dest with ; on Windows
$datas = @(
    "background.jpg;.",
    "bar.png;.",
    "box.png;.",
    "button.png;.",
    "cage.png;.",
    "character-moving.png;.",
    "character-standing.png;.",
    "cheese.png;.",
    "circuit-1.png;.",
    "circuit-2.png;.",
    "circuit-3.png;.",
    "circuit-4.png;.",
    "level-1.png;.",
    "level-2.png;.",
    "level-3.png;.",
    "level-4.png;.",
    "level-5.png;.",
    "level-bg.png;.",
    "level-selection-bg.png;.",
    "lose-bg.png;.",
    "platform.png;.",
    "rock-big.png;.",
    "rock-small.png;.",
    "splash.png;.",
    "summary-instructions.png;.",
    "tutorial-bg.png;.",
    "win-bg.png;.",
    "font;font",
    "assets;assets",
    "audio\\audio_config.json;audio"
)

# Assemble args
$addDataArgs = @()
foreach ($d in $datas) { $addDataArgs += @('--add-data', $d) }

# Optional: custom icon (uncomment and set if you add one)
$iconArg = @()
# $iconArg = @('--icon', 'icon.ico')

# Build
& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --name "CheeseGates" `
    --onefile `
    --windowed `
    @iconArg `
    @addDataArgs `
    main.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

Write-Host "Build complete. EXE at: dist/CheeseGates.exe"
