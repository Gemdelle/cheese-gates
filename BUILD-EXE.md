# Construir el ejecutable (.exe) tras cada cambio

Este proyecto incluye un script que empaqueta el juego con PyInstaller e incluye todos los assets necesarios.

## Requisitos
- Windows 10/11 (64-bit)
- Python 3.13 (o el que uses en el repo)
- PowerShell

## 1) (Opcional) Crear/activar entorno virtual
```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

## 2) Construir el .exe
El script se encarga de instalar dependencias, limpiar build previos, y empaquetar en onefile/windowed.
```powershell
# Ubícate en la carpeta del proyecto
Set-Location \cheese-gates

# Ejecuta el build
.\build_exe.ps1
```
Salida esperada:
- Ejecutable en `dist/CheeseGates.exe`

## 3) Probar el ejecutable
```powershell
Set-Location \cheese-gates
.\dist\CheeseGates.exe
```

## 4) ¿Qué incluye el paquete?
- Imágenes y recursos del directorio raíz (png/jpg)
- Carpeta `assets/` (música y sonidos)
- Carpeta `font/`
- `audio/audio_config.json`
- Ajuste de rutas para ejecutable (usa `sys._MEIPASS`)

## 5) Persistencia de configuración
- El archivo `settings.json` se guarda en:
  - Windows: `%APPDATA%\CheeseGates\settings.json`

## 6) Reconstruir tras cambios
Cada vez que modifiques código o assets, vuelve a ejecutar:
```powershell
.\build_exe.ps1
```
El script limpia `build/` y `dist/` automáticamente para generar un binario fresco.

## 7) Opcional: icono del ejecutable
- Coloca `icon.ico` en la raíz y descomenta la línea del icono en `build_exe.ps1`:
  - `# $iconArg = @('--icon', 'icon.ico')` -> ` $iconArg = @('--icon', 'icon.ico')`
- Vuelve a ejecutar el build.

## 8) Distribución a usuarios finales
- Comparte `dist/CheeseGates.exe` (puedes comprimirlo en `.zip`).
- SmartScreen puede aparecer: “Más información” > “Ejecutar de todas formas”.

## 9) Solución de problemas
- ¿No suena audio? Verifica que `assets/` esté incluido (el script lo agrega), y que tu audio no esté silenciado en `Settings` del juego.
- ¿No carga una imagen/fuente? Asegúrate de que el archivo exista en el repo y, si es un nuevo asset fuera de `assets/` o `font/`, agrégalo a la lista `$datas` en `build_exe.ps1`.
- Si cambiaste la versión de Python, reinstala dependencias: `pip install -r requirements.txt` (el build ya lo hace).
