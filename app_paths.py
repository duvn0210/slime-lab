"""Rutas del juego en código fuente y en el .exe empaquetado."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent
