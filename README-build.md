# Empaquetar el juego como .exe (Windows)

Sigue estos pasos en Windows (PowerShell):

1. (Opcional) Crear y activar un entorno virtual:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Instalar dependencias y construir el .exe:
   ./build_exe.ps1

El ejecutable resultante estará en `dist/CheeseGates.exe`.

Notas:
- El script incluye assets, fuentes, y `audio/audio_config.json`.
- En modo empaquetado, `main.py` ajusta el directorio de trabajo a `sys._MEIPASS` para que las rutas relativas a imágenes/sonidos funcionen.
- Si agregas nuevos assets, añade sus rutas a `build_exe.ps1` en la sección `$datas`.
