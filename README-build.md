# Ejecutar y empaquetar el juego (Windows)

Guía rápida de comandos en PowerShell para correr el juego en desarrollo y generar el `.exe` distribuible.

## Modo desarrollo (sin empaquetar)

Primera vez (crear venv e instalar dependencias):

```powershell
py -3 -m venv venv
.\n+venv\Scripts\python.exe -m pip install -r requirements.txt
.
venv\Scripts\python.exe .\main.py
```

Siguientes veces (solo ejecutar):

```powershell
.
venv\Scripts\python.exe .\main.py
```

## Empaquetar con PyInstaller

Usa el script `build_exe.ps1` (crea/usa `.\venv` automáticamente si hace falta). Hay tres modos:

- release (defecto): build limpio, `--onefile`, instala dependencias. Ideal para publicar.
- fast: reutiliza caché, `--onefile`, no instala deps por defecto. Rápido para iterar.
- dev: reutiliza caché, `--onedir` (carpeta), no instala deps por defecto. El más veloz.

Comandos:

```powershell
# Release completo (limpia, instala deps, EXE único)
.\n+build_exe.ps1

# Build rápido (onefile, sin limpiar, sin reinstalar deps)
.
build_exe.ps1 -Mode fast -SkipDeps

# Build ultra-rápido (carpeta onedir, ideal para iterar)
.
build_exe.ps1 -Mode dev -SkipDeps

# Forzar instalación de deps en fast/dev
.
build_exe.ps1 -Mode fast -SkipDeps:$false

# Usar icono personalizado
.
build_exe.ps1 -Mode fast -SkipDeps -Icon .\icon.ico
```

Salida:

- release / fast: `dist/CheeseGates.exe`
- dev: carpeta `dist/CheeseGates-Dev/` (ejecutar `CheeseGates-Dev.exe` dentro)

## Ejecutar como usuario final (sin Python)

Entrega/ejecuta el build: 

```powershell
.
dist\CheeseGates.exe
```

No requiere Python instalado.

## Notas

- El build incluye assets, fuentes y `audio/audio_config.json`.
- En el `.exe`, `main.py` ajusta las rutas relativas (via `sys._MEIPASS`).
- Nuevas imágenes en la raíz del repo (PNG/JPG/JPEG/GIF/BMP/WEBP) se empaquetan automáticamente.
- Para otros assets, colócalos dentro de `assets/` o `font/` (ambas carpetas se incluyen); si creas nuevas carpetas raíz, añádelas a `$datas` en `build_exe.ps1`.

### Silenciar advertencias libpng (iCCP)

El juego suprime por defecto la advertencia `libpng warning: iCCP: known incorrect sRGB profile` tanto en desarrollo como en el `.exe`.

- Toggle por variable de entorno: `CHEESEGATES_SUPPRESS_LIBPNG`
	- `1` (o ausente): suprime la advertencia (comportamiento por defecto)
	- `0`: no suprime (muestra la advertencia)

Ejemplos PowerShell:

```powershell
# Dev run suprimiendo (por defecto ya está suprimido)
$env:CHEESEGATES_SUPPRESS_LIBPNG = '1'
.
venv\Scripts\python.exe .\main.py

# Dev run mostrando advertencia
$env:CHEESEGATES_SUPPRESS_LIBPNG = '0'
.
venv\Scripts\python.exe .\main.py

# Ejecutar el EXE suprimiendo (por defecto)
$env:CHEESEGATES_SUPPRESS_LIBPNG = '1'
.
dist\CheeseGates.exe

# Ejecutar el EXE mostrando la advertencia
$env:CHEESEGATES_SUPPRESS_LIBPNG = '0'
.
dist\CheeseGates.exe
```
