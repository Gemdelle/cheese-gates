"""
Módulo simple para persistir ajustes del juego en un archivo JSON local.

- Guarda/lee: resolución, modo de ventana, audio y modo daltónico.
- Archivo: settings.json en el mismo directorio del juego.
"""
import json
import os
from typing import Dict, Optional


def _config_path() -> str:
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
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # En caso de error de IO, no interrumpir el juego
        pass
