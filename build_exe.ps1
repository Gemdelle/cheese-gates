# Builds a standalone Windows .exe with PyInstaller
# Usage: Run this script in PowerShell from the repo root

$ErrorActionPreference = 'Stop'

# Ensure we're at the script location (repo root)
Set-Location -Path $PSScriptRoot

# Create a clean dist/build
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }

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
    Write-Host "No se encontró Python en este sistema. Para COMPILAR necesitas Python instalado (3.11+)." -ForegroundColor Yellow
    Write-Host "Opciones:" -ForegroundColor Yellow
    Write-Host "  1) Instala Python desde https://www.python.org/downloads/ y marca 'Add Python to PATH'." -ForegroundColor Yellow
    Write-Host "  2) O usa el ejecutable ya construido en .\\dist\\CheeseGates.exe (no requiere Python)." -ForegroundColor Yellow
    throw "Python no encontrado. Cancelando build."
}

# Crear venv si no existe aún (para builds reproducibles)
if (-not (Test-Path .\venv\Scripts\python.exe)) {
    Write-Host "Creando entorno virtual en .\\venv..."
    & "$python" -m venv venv
    $python = (Resolve-Path .\venv\Scripts\python.exe).Path
}

Write-Host "Using Python: $python"

# Instalar dependencias
& "$python" -m pip install --upgrade pip
& "$python" -m pip install -r requirements.txt

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
& "$python" -m PyInstaller `
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
