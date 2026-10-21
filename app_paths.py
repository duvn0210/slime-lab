"""
app_paths.py — dónde están las imágenes.

Para qué sirve:
    Devuelve la carpeta raíz del juego para cargar `assets/`.

Conectado con:
    - assets_loader.py (única quien lo usa hoy)
    - main.py no lo llama directo

Si alguien pregunta “¿por qué no Path(__file__) a secas?”:
    En un .exe empaquetado __file__ no apunta a la carpeta del proyecto.
    PyInstaller deja los archivos en sys._MEIPASS. Esta función cubre ambos casos.
"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_dir() -> Path:
    """Carpeta que contiene `assets/` tanto al correr con Python como en un .exe."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent
