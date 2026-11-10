"""
Música de fondo y clics de botones y teclas.

Si existe assets/musica.ogg (también sirve .mp3 o .wav), esa canción
suena en bucle. Si no hay archivo, suena una melodía hecha en el código.
El parlante de la barra apaga la música y los efectos a la vez.
"""

from __future__ import annotations

import math
import struct

import pygame

from app_paths import resource_dir

RATE = 44100


def _samples(freq: float, ms: int, volume: float) -> list[int]:
    """Nota grave y redonda: el tono principal más un poco de la octava de abajo."""
    count = max(1, int(RATE * ms / 1000))
    values = []
    for i in range(count):
        fade_in = min(1.0, i / max(1, count * 0.12))
        fade_out = (1.0 - i / count) ** 1.4
        t = i / RATE
        wave = math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(2 * math.pi * freq * 0.5 * t)
        sample = int(volume * 24000 * fade_in * fade_out * wave)
        values.append(max(-32767, min(32767, sample)))
    return values


def _bubble(start: float, ms: int, volume: float) -> list[int]:
    """Burbuja: el tono baja rápido, como una gota, y no se queda pitando."""
    count = max(1, int(RATE * ms / 1000))
    values = []
    phase = 0.0
    for i in range(count):
        t = i / count
        freq = start * (1.0 - 0.62 * t)
        phase += 2 * math.pi * freq / RATE
        env = math.sin(math.pi * min(1.0, i / max(1, count * 0.18))) * math.exp(-3.2 * t)
        sample = int(volume * 24000 * math.sin(phase) * env)
        values.append(max(-32767, min(32767, sample)))
    return values


def _stereo(values: list[int]) -> bytes:
    """El mezclador va en estéreo: el mismo sonido en los dos lados."""
    return b"".join(struct.pack("<hh", sample, sample) for sample in values)


def _song_file():
    """La canción de fondo, si la dejaron en assets. Si no hay archivo, no hay canción."""
    folder = resource_dir() / "assets"
    for name in ("musica.ogg", "musica.mp3", "musica.wav"):
        path = folder / name
        if path.is_file():
            return path
    return None


def _melody() -> bytes:
    """Loop grave, en el registro de un xilófono pequeño, para no pitar en audífonos."""
    notes = (
        (196, 340),
        (247, 340),
        (294, 340),
        (247, 340),
        (262, 340),
        (330, 480),
        (294, 340),
        (196, 640),
        (220, 340),
        (262, 340),
        (330, 480),
        (247, 760),
    )
    gap = [0] * int(RATE * 0.04)
    song: list[int] = []
    for freq, ms in notes:
        song.extend(_samples(freq, ms, 0.22))
        song.extend(gap)
    song.extend([0] * int(RATE * 0.35))
    return _stereo(song)


class Sfx:
    """Música en bucle y dos efectos. Si no hay audio, el juego sigue igual."""

    def __init__(self) -> None:
        self.ready = False
        self.music = None
        self.song = None
        self.click = None
        self.key = None
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(RATE, -16, 2, 1024)
            pygame.mixer.set_num_channels(8)
            pygame.mixer.set_reserved(1)
            self.song = _song_file()
            if self.song is None:
                self.music = pygame.mixer.Sound(buffer=_melody())
            self.click = pygame.mixer.Sound(buffer=_stereo(_bubble(620, 180, 0.4)))
            self.key = pygame.mixer.Sound(buffer=_stereo(_bubble(480, 120, 0.28)))
            self.ready = True
            self.set_enabled(True)
        except pygame.error:
            self.ready = False

    def set_enabled(self, enabled: bool) -> None:
        """Enciende o apaga música y, al encender, hace un clic para confirmar."""
        if not self.ready:
            return
        if self.song is not None:
            if enabled:
                pygame.mixer.music.load(str(self.song))
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(loops=-1)
            else:
                pygame.mixer.music.stop()
            self.play("click", enabled)
            return
        if self.music is None:
            return
        channel = pygame.mixer.Channel(0)
        if enabled:
            channel.set_volume(0.4)
            if not channel.get_busy():
                channel.play(self.music, loops=-1)
            self.play("click", True)
        else:
            channel.stop()

    def play(self, kind: str, enabled: bool) -> None:
        """kind es 'key' (teclado) o 'click' (mouse). enabled es el parlante."""
        if not self.ready or not enabled:
            return
        sound = self.key if kind == "key" else self.click
        if sound is not None:
            sound.play()
