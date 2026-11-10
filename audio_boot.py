"""
En Linux a veces Pygame no encuentra la librería de PulseAudio, aunque
viene dentro del propio Pygame. Esto le deja el camino listo antes de
abrir el mezclador. En Windows no hace nada.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def prepare_linux_audio() -> None:
    """Si hace falta, reinicia el programa con la librería de audio a la vista."""
    if os.name != "posix":
        return
    simple = None
    for entry in sys.path:
        libs = Path(entry) / "pygame.libs"
        if not libs.is_dir():
            continue
        found = sorted(libs.glob("libpulse-simple*.so*"))
        if found:
            simple = found[0]
            break
    if simple is None:
        return
    stub = Path(__file__).resolve().parent / ".audio-libs"
    stub.mkdir(exist_ok=True)
    link = stub / "libpulse-simple.so.0"
    if not link.is_symlink():
        if link.exists():
            link.unlink()
        link.symlink_to(simple)
    stub_text = str(stub)
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if stub_text in current.split(":"):
        return
    os.environ["LD_LIBRARY_PATH"] = stub_text + (":" + current if current else "")
    os.execv(sys.executable, [sys.executable, *sys.argv])
