param(
    [ValidateSet('release','fast','dev')]
    [string]$Mode = 'release',
    [switch]$SkipDeps,
    [string]$Icon
)

# Builds a Windows package with PyInstaller
# Modes:
#   release (default): clean build, onefile EXE, install deps
#   fast:              reuse cache, onefile EXE, skip deps by default
#   dev:               reuse cache, onedir folder (fastest), skip deps by default
# Usage examples:
#   .\build_exe.ps1                              # full release build
#   .\build_exe.ps1 -Mode fast -SkipDeps         # quicker onefile build (no clean)
#   .\build_exe.ps1 -Mode dev  -SkipDeps         # fastest onedir build for local testing
#   .\build_exe.ps1 -Icon .\icon.ico            # release with custom icon

$ErrorActionPreference = 'Stop'

# Ensure we're at the script location (repo root)
Set-Location -Path $PSScriptRoot

# Determine behavior by mode
$isRelease = ($Mode -eq 'release')
$isFast    = ($Mode -eq 'fast')
$isDev     = ($Mode -eq 'dev')

# Cleaning policy
$doClean = $isRelease
if ($doClean) {
    if (Test-Path build) { Remove-Item -Recurse -Force build }
    if (Test-Path dist)  { Remove-Item -Recurse -Force dist }
}

function Resolve-PythonPath {
    # 1) Prefer local venv
    if (Test-Path .\venv\Scripts\python.exe) { return (Resolve-Path .\venv\Scripts\python.exe).Path }
    if (Test-Path .\.venv\Scripts\python.exe) { return (Resolve-Path .\.venv\Scripts\python.exe).Path }

    # 2) Try Windows 'py' launcher with common versions
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        foreach ($v in @('3.13','3.12','3.11','3.10','3')) {
            try {
                $out = & $py.Path -$v -c "import sys;print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $out) { return $out.Trim() }
            } catch {}
        }
    }

    # 3) Try python in PATH
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Path }

    # 4) where.exe fallback
    try {
        $where = & where.exe python 2>$null
        if ($where) { return ($where -split "`r?`n")[0] }
    } catch {}

    return $null
}

$python = Resolve-PythonPath
if (-not $python) {
    Write-Host "Python not found. To BUILD you need Python installed (3.11+)." -ForegroundColor Yellow
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1) Install Python from https://www.python.org/downloads/ and check 'Add Python to PATH'." -ForegroundColor Yellow
    Write-Host "  2) Or use the pre-built executable in .\dist\CheeseGates.exe (no Python required)." -ForegroundColor Yellow
    throw "Python not found. Cancelling build."
}

# Create venv if it doesn't exist (for reproducible builds)
if (-not (Test-Path .\venv\Scripts\python.exe)) {
    Write-Host "Creating virtual environment in .\venv..."
    & "$python" -m venv venv
    $python = (Resolve-Path .\venv\Scripts\python.exe).Path
}

Write-Host "Using Python: $python"

# Install dependencies
# - release: always installs
# - fast/dev: by default does NOT install; use without -SkipDeps to force install
if ($isRelease -or -not $SkipDeps) {
    Write-Host "Installing dependencies..."
    & "$python" -m pip install --upgrade pip
    & "$python" -m pip install -r requirements.txt
} else {
    Write-Host "Skipping dependency install (SkipDeps enabled)." -ForegroundColor Yellow
}

# Collect data files (auto-add new top-level images + known folders)
# PyInstaller --add-data needs src;dest with ; on Windows
$datas = @(
    "font;font",
    "assets;assets",
    "audio\audio_config.json;audio"
)

# Auto-include any image files at repo root
$rootImageExts = @('*.png','*.jpg','*.jpeg','*.gif','*.bmp','*.webp')
try {
    $rootImages = Get-ChildItem -Path $PSScriptRoot -File -Include $rootImageExts -Name -ErrorAction SilentlyContinue
    foreach ($f in $rootImages) {
        $datas += "${f};."
    }
} catch {}

# Assemble args
$addDataArgs = @()
foreach ($d in $datas) { $addDataArgs += @('--add-data', $d) }

# Optional: custom icon (resolve relative to script root; skip if missing)
$iconArg = @()
if ($Icon) {
    $iconPath = $Icon
    if (-not [System.IO.Path]::IsPathRooted($iconPath)) {
        $iconPath = Join-Path $PSScriptRoot $iconPath
    }
    if (Test-Path $iconPath) {
        $iconArg = @('--icon', (Resolve-Path $iconPath).Path)
    } else {
        Write-Host "Icon not found: $iconPath - building without custom icon." -ForegroundColor Yellow
        $iconArg = @()
    }
}

# Bundle mode
$bundleArg = @('--onefile')
if ($isDev) { $bundleArg = @('--onedir') }

# Clean arg
$cleanArg = @()
if ($doClean) { $cleanArg = @('--clean') }

# Name
$appName = if ($isDev) { 'CheeseGates-Dev' } else { 'CheeseGates' }

# Build
& "$python" -m PyInstaller `
    --noconfirm `
    @cleanArg `
    --name $appName `
    @bundleArg `
    --windowed `
    @iconArg `
    @addDataArgs `
    main.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

if ($isDev) {
    Write-Host "Build complete. App folder at: dist/$appName" -ForegroundColor Green
} elseif ($isFast) {
    Write-Host "Build complete (fast). EXE at: dist/$appName.exe" -ForegroundColor Green
} else {
    Write-Host "Build complete. EXE at: dist/$appName.exe" -ForegroundColor Green
}
