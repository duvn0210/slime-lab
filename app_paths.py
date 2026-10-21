"""
Ayuda chiquita: “¿en qué carpeta están las fotos?”.

Normalmente es la carpeta del proyecto (donde está main.py).
Si algún día el juego se empaqueta en un .exe, las fotos viajan dentro
del programa; esta función también encuentra esa carpeta.
Lo usa assets_loader.py al cargar fondo_slime.jpg y los clientes.
"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_dir() -> Path:
    """Devuelve la carpeta donde está la carpeta assets (fotos del laboratorio y de los clientes)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent
