"""
Módulo simple para persistir ajustes del juego en un archivo JSON local.

- Guarda/lee: resolución, modo de ventana, audio y modo daltónico.
- Archivo: settings.json en el mismo directorio del juego.
"""
import json
import os
import sys
from typing import Dict, Optional


def _config_path() -> str:
    """Return path to settings.json.
    - In frozen (PyInstaller) mode, use a writable user dir (APPDATA on Windows).
    - In dev mode, keep it next to the source for simplicity.
    """
    # Frozen EXE: write to user data dir
    if getattr(sys, "frozen", False):
        # Windows: %APPDATA%\CheeseGates; Others: ~/.cheese_gates
        if os.name == "nt":
            appdata = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
            base = os.path.join(appdata, "CheeseGates")
        else:
            base = os.path.join(os.path.expanduser("~"), ".cheese_gates")
        try:
            os.makedirs(base, exist_ok=True)
        except Exception:
            pass
        return os.path.join(base, "settings.json")
    # Dev: alongside source
    base = os.path.dirname(__file__)
    return os.path.join(base, "settings.json")


def load_settings() -> Optional[Dict[str, str]]:
    """Cargar ajustes desde settings.json; devuelve None si no existe o está corrupto."""
    path = _config_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None


def save_settings(data: Dict[str, str]) -> None:
    """Guardar ajustes a settings.json (sobrescribe)."""
    path = _config_path()
    # Make sure directory exists (in case of user dir)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # En caso de error de IO, no interrumpir el juego
        pass
