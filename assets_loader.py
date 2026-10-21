"""
assets_loader.py — carga de imágenes, fuentes e iconos.

Para qué sirve:
    Pone el fondo (fondo_slime.jpg), escala los PNG de clientes y dibuja
    una “hoja” de iconos de 48 px (moneda, matraz, glitter…). En Windows,
    si no hay DejaVu, usa Arial.

Conectado con:
    - main.py crea un AssetLoader
    - ORDER y RESULT llaman draw_customer
    - app_paths.resource_dir  (carpeta assets/)
    - settings WIDTH/HEIGHT

El vaso animado que se ve en BUILD/MIX/TOP NO está aquí: está en
ui_components.Beaker. Abajo hay un draw_beaker viejo que las estaciones
ya no usan; no confundirlo.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pygame

from app_paths import resource_dir
from settings import BOTTOM_BAR_H, C, HEIGHT, TOP_BAR_H, WIDTH

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
ICON_NAMES = ("coin", "flask", "glitter", "star", "seal", "safety", "lid", "drop")


def _font(path: str, size: int, fallback_bold: bool = False) -> pygame.font.Font:
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("arial", size, bold=fallback_bold)


def tint(color: tuple[int, int, int], amount: float, toward=(255, 255, 255)) -> tuple[int, int, int]:
    return tuple(int(color[i] * (1 - amount) + toward[i] * amount) for i in range(3))


def shade(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(max(0, int(color[i] * (1 - amount))) for i in range(3))


class AssetLoader:
    def __init__(self) -> None:
        self.xs = _font(FONT_REGULAR, 13)
        self.sm = _font(FONT_REGULAR, 14)
        self.md = _font(FONT_BOLD, 16, True)
        self.lg = _font(FONT_BOLD, 22, True)
        self.xl = _font(FONT_BOLD, 32, True)
        self.mono = _font(FONT_MONO, 14)
        self.tiny = _font(FONT_REGULAR, 12)
        self.background = self._load_background()
        self.clients = self._load_clients()
        self.sheet = self._make_sheet()
        self.icons = self._slice_icons()
        self.bubble_zones = (
            pygame.Rect(48, 210, 70, 150),
            pygame.Rect(900, 200, 74, 160),
            pygame.Rect(250, 250, 40, 90),
            pygame.Rect(730, 240, 46, 100),
        )

    def _asset_path(self, name: str) -> Path:
        return resource_dir() / "assets" / name

    def _load_background(self) -> pygame.Surface:
        """Ilustración limpia del laboratorio, a tamaño de ventana."""
        raw = pygame.image.load(str(self._asset_path("fondo_slime.jpg"))).convert()
        return pygame.transform.smoothscale(raw, (WIDTH, HEIGHT))

    def _load_clients(self) -> dict[str, pygame.Surface]:
        files = {
            "customer": "customer.png",
            "mia": "client_mia.png",
            "zack": "client_zack.png",
            "layla": "client_layla.png",
            "ben": "client_ben.png",
        }
        play = HEIGHT - TOP_BAR_H - BOTTOM_BAR_H
        clients = {}
        for key, name in files.items():
            raw = pygame.image.load(str(self._asset_path(name))).convert_alpha()
            if key == "customer":
                target_h = min(268, play - 20)
                target_w = max(1, int(raw.get_width() * target_h / raw.get_height()))
            else:
                target_w = 170
                target_h = max(1, int(raw.get_height() * target_w / raw.get_width()))
                if target_h > play - 16:
                    target_h = play - 16
                    target_w = max(1, int(raw.get_width() * target_h / raw.get_height()))
            clients[key] = pygame.transform.smoothscale(raw, (target_w, target_h))
        return clients

    def blit_background(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))

    def draw_station(self, surface: pygame.Surface, station: str) -> None:
        self.blit_background(surface)

    def draw_lab(self, surface: pygame.Surface, time: float) -> None:
        self.blit_background(surface)

    def draw_customer(self, surface: pygame.Surface, order, mood: str = "ok") -> None:
        """Sprite del cliente recortado, esquina inferior izquierda."""
        key = getattr(order, "sprite", "customer")
        sprite = self.clients.get(key, self.clients["customer"]).copy()
        self._apply_mood(sprite, key, mood)
        x = 8
        y = HEIGHT - BOTTOM_BAR_H - sprite.get_height() + 10
        surface.blit(sprite, (x, y))
        label = self.sm.render(order.name, True, (34, 34, 34))
        chip = label.get_rect()
        chip.midbottom = (x + sprite.get_width() // 2, HEIGHT - BOTTOM_BAR_H - 6)
        plate = chip.inflate(14, 6)
        layer = pygame.Surface(plate.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, (255, 255, 255, 220), layer.get_rect(), border_radius=10)
        surface.blit(layer, plate.topleft)
        surface.blit(label, chip)

    def _apply_mood(self, sprite, key: str, mood: str) -> None:
        if mood == "ok":
            return
        mouth = {
            "customer": (0.50, 0.46),
            "mia": (0.62, 0.42),
            "zack": (0.58, 0.46),
            "layla": (0.62, 0.40),
            "ben": (0.64, 0.42),
        }.get(key, (0.58, 0.44))
        mx = int(sprite.get_width() * mouth[0])
        my = int(sprite.get_height() * mouth[1])
        sample = sprite.get_at((mx, max(0, my - 10)))
        cover = pygame.Rect(0, 0, 34, 16)
        cover.center = (mx, my)
        pygame.draw.ellipse(sprite, sample, cover)
        arc = pygame.Rect(0, 0, 28, 16)
        arc.center = (mx, my + (2 if mood == "sad" else 1))
        if mood == "sad":
            pygame.draw.arc(sprite, (70, 32, 40), arc, 0.25, math.pi - 0.25, 3)
        else:
            pygame.draw.arc(sprite, (70, 32, 40), arc, math.pi + 0.2, math.tau - 0.2, 3)

    def draw_bubble(self, surface: pygame.Surface, x: int, y: int, time: float) -> None:
        radius = int(42 + math.sin(time * 3) * 2)
        tail = [(x - 4, y + radius - 12), (x + 12, y + radius - 8), (x - 16, y + radius + 20)]
        pygame.draw.polygon(surface, C["white"], tail)
        pygame.draw.circle(surface, C["white"], (x, y), radius)
        pygame.draw.circle(surface, C["ink"], (x, y), radius, 3)
        icon = pygame.transform.smoothscale(self.icons["flask"], (46, 46))
        surface.blit(icon, (x - 23, y - 24))

    def draw_beaker(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        liquid_color: tuple[int, int, int],
        fill: float,
        time: float,
        *,
        show_agitator: bool = False,
        angle: float = 0.0,
        mixing: bool = False,
        toppings: set[str] | None = None,
    ) -> pygame.Rect:
        toppings = toppings or set()
        base_h = 34
        glass = pygame.Rect(rect.x, rect.y, rect.w, rect.h - base_h)
        inner = glass.inflate(-22, -18)
        inner.y += 6
        platform = pygame.Rect(rect.x - 18, rect.bottom - base_h + 4, rect.w + 36, 20)
        foot = pygame.Rect(platform.x + 28, platform.bottom - 2, platform.w - 56, 8)
        pygame.draw.rect(surface, (70, 76, 88), foot, border_radius=4)
        pygame.draw.rect(surface, (168, 176, 186), platform, border_radius=6)
        pygame.draw.rect(surface, (90, 98, 110), platform, width=2, border_radius=6)

        body = pygame.Surface(glass.size, pygame.SRCALPHA)
        pygame.draw.rect(body, (255, 255, 255, 35), body.get_rect(), border_radius=20)
        surface.blit(body, glass.topleft)

        fill = max(0.08, min(0.94, fill))
        liquid_h = int(inner.h * fill)
        liquid = pygame.Rect(inner.x, inner.bottom - liquid_h, inner.w, liquid_h)
        prev = surface.get_clip()
        surface.set_clip(inner)
        deep = shade(liquid_color, 0.18)
        pygame.draw.rect(surface, deep, liquid)
        band = pygame.Rect(liquid.x, liquid.y, liquid.w, max(8, liquid.h // 3))
        pygame.draw.rect(surface, liquid_color, band)
        wave = 4 + (3 if mixing else 1) * math.sin(time * (4 if mixing else 2))
        meniscus = pygame.Rect(liquid.x - 2, int(liquid.y - 10 + wave), liquid.w + 4, 22)
        pygame.draw.ellipse(surface, tint(liquid_color, 0.35), meniscus)
        bubbles = 10 if mixing else 4
        for i in range(bubbles):
            cycle = 1.4 + (i % 5) * 0.25
            phase = (time * (1.6 if mixing else 0.7) / cycle + i * 0.13) % 1.0
            bx = liquid.x + 10 + int((i * 29) % max(1, liquid.w - 16))
            by = liquid.bottom - 8 - int(phase * max(8, liquid.h - 12))
            pygame.draw.circle(surface, tint(liquid_color, 0.55), (bx, by), 2 + i % 3, 1)
        if mixing:
            for k in range(3):
                swirl = liquid.inflate(-16, -10)
                start = angle + k * 2.1
                pygame.draw.arc(surface, tint(liquid_color, 0.72), swirl, start, start + 1.1, 3)
        if "glitter" in toppings:
            for i in range(14):
                gx = liquid.x + 8 + int((i * 23 + 5) % max(1, liquid.w - 12))
                gy = liquid.y + 8 + int((i * 17) % max(1, liquid.h - 10))
                spark = (255, 255, 255) if (i + int(time * 6)) % 2 == 0 else C["gold"]
                pygame.draw.circle(surface, spark, (gx, gy), 2)
        if "stars" in toppings:
            for i, (fx, fy) in enumerate(((0.3, 0.4), (0.62, 0.55), (0.45, 0.72))):
                sx = liquid.x + int(liquid.w * fx)
                sy = liquid.y + int(liquid.h * fy + math.sin(time * 2 + i) * 3)
                self._star(surface, sx, sy, 7, C["gold"])
        surface.set_clip(prev)

        outline = pygame.Surface(glass.size, pygame.SRCALPHA)
        pygame.draw.rect(outline, (236, 244, 255, 210), outline.get_rect(), width=3, border_radius=20)
        pygame.draw.line(outline, (255, 255, 255, 180), (14, 24), (14, glass.h - 28), 3)
        surface.blit(outline, glass.topleft)
        for mark in range(1, 6):
            my = inner.bottom - int(inner.h * mark / 5)
            pygame.draw.line(surface, (80, 90, 110), (inner.right - 16, my), (inner.right - 4, my), 2)

        lip = pygame.Rect(glass.x - 8, glass.y - 8, glass.w + 16, 20)
        pygame.draw.ellipse(surface, (214, 224, 236), lip)
        pygame.draw.ellipse(surface, (255, 255, 255), lip, 2)

        if "lid" in toppings:
            cap = pygame.Rect(glass.x - 4, glass.y - 16, glass.w + 8, 24)
            pygame.draw.ellipse(surface, (86, 96, 120), cap)
            pygame.draw.ellipse(surface, (210, 216, 230), cap.inflate(-18, -8))
        if show_agitator and "lid" not in toppings:
            self._draw_agitator(surface, glass, liquid, angle, mixing)
        if "seal" in toppings:
            badge = pygame.Rect(glass.right - 36, glass.bottom - 70, 28, 28)
            pygame.draw.circle(surface, (72, 150, 230), badge.center, 14)
            pygame.draw.circle(surface, C["white"], badge.center, 14, 2)
            pygame.draw.line(surface, C["white"], (badge.centerx - 6, badge.centery), (badge.centerx - 1, badge.centery + 5), 2)
            pygame.draw.line(surface, C["white"], (badge.centerx - 1, badge.centery + 5), (badge.centerx + 7, badge.centery - 5), 2)
        if "safety" in toppings:
            self._triangle(surface, glass.x - 28, glass.y + 36, 22, (255, 186, 48))
        return glass

    def _draw_agitator(self, surface, glass, liquid, angle, mixing) -> None:
        motor = pygame.Rect(glass.centerx - 22, glass.y - 34, 44, 26)
        pygame.draw.rect(surface, (70, 78, 96), motor, border_radius=6)
        pygame.draw.circle(surface, (255, 196, 64) if mixing else (150, 160, 170), (motor.centerx, motor.centery), 5)
        shaft_bottom = max(liquid.y + 16, glass.y + 30)
        pygame.draw.line(surface, (90, 98, 112), (glass.centerx, motor.bottom), (glass.centerx, shaft_bottom), 4)
        blade = 28
        dx = math.cos(angle) * blade
        dy = math.sin(angle) * 8
        yb = shaft_bottom
        pygame.draw.line(surface, (60, 68, 82), (glass.centerx - dx, yb - dy), (glass.centerx + dx, yb + dy), 4)
        pygame.draw.circle(surface, (60, 68, 82), (glass.centerx, yb), 4)

    def _make_background(self) -> pygame.Surface:
        """Laboratorio cartoon dibujado a resolución de ventana, sin texto ni controles."""
        surf = pygame.Surface((WIDTH, HEIGHT))
        top = (72, 54, 168)
        bot = (126, 176, 220)
        for y in range(HEIGHT):
            t = y / max(1, HEIGHT - 1)
            col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(surf, col, (0, y), (WIDTH, y))
        for col in range(80, WIDTH, 160):
            pygame.draw.circle(surf, (255, 255, 255), (col, 150), 46, 3)
            pygame.draw.circle(surf, (186, 210, 240), (col, 150), 28, 2)
        bench = HEIGHT - BOTTOM_BAR_H - 22
        pygame.draw.rect(surf, (36, 168, 186), (0, bench, WIDTH, HEIGHT - bench))
        pygame.draw.rect(surf, (18, 110, 132), (0, bench, WIDTH, 8))
        self._reactor(surf, pygame.Rect(-10, 168, 96, bench - 176), (72, 206, 214), (170, 240, 236))
        self._reactor(surf, pygame.Rect(WIDTH - 86, 168, 96, bench - 176), (214, 110, 176), (255, 186, 214))
        self._pipes(surf)
        return surf

    def _reactor(self, surf, rect, liquid, glow) -> None:
        pygame.draw.rect(surf, (86, 48, 120), rect, border_radius=24)
        pygame.draw.rect(surf, (230, 220, 245), rect, width=4, border_radius=24)
        inner = rect.inflate(-28, -36)
        inner.y += 8
        pygame.draw.rect(surf, shade(liquid, 0.25), inner, border_radius=12)
        level = pygame.Rect(inner.x, inner.y + inner.h // 3, inner.w, inner.h * 2 // 3)
        pygame.draw.rect(surf, liquid, level, border_radius=10)
        pygame.draw.ellipse(surf, glow, (level.x, level.y - 8, level.w, 18))
        dome = pygame.Rect(rect.x + 20, rect.y - 24, rect.w - 40, 40)
        pygame.draw.ellipse(surf, (200, 190, 220), dome)
        pygame.draw.rect(surf, (70, 48, 96), (rect.centerx - 6, rect.y - 48, 12, 30))

    def _cabinet(self, surf, rect) -> None:
        pygame.draw.rect(surf, (92, 48, 140), rect, border_radius=10)
        pygame.draw.rect(surf, (220, 200, 240), rect, width=3, border_radius=10)
        door = rect.inflate(-16, -18)
        pygame.draw.rect(surf, (170, 210, 235), door, border_radius=6)
        pygame.draw.line(surf, (236, 248, 255), (door.x + 8, door.y + 8), (door.x + 8, door.bottom - 8), 2)
        pygame.draw.circle(surf, C["gold"], (door.right - 10, door.centery), 4)

    def _pipes(self, surf) -> None:
        color = (236, 244, 255)
        pygame.draw.arc(surf, color, (150, 78, 200, 90), 0, math.pi, 6)
        pygame.draw.arc(surf, (255, 190, 220), (WIDTH - 360, 78, 200, 90), 0, math.pi, 6)
        pygame.draw.line(surf, color, (190, 122), (190, 190), 6)
        pygame.draw.line(surf, (255, 190, 220), (WIDTH - 220, 122), (WIDTH - 220, 190), 6)
        pygame.draw.circle(surf, (230, 230, 240), (190, 198), 8)
        pygame.draw.circle(surf, (80, 80, 100), (190, 198), 8, 2)

    def _make_sheet(self) -> pygame.Surface:
        sheet = pygame.Surface((48 * len(ICON_NAMES), 48), pygame.SRCALPHA)
        for index, name in enumerate(ICON_NAMES):
            cell = pygame.Rect(index * 48, 0, 48, 48)
            getattr(self, f"_icon_{name}")(sheet, cell)
        return sheet

    def _slice_icons(self) -> dict[str, pygame.Surface]:
        icons = {}
        for index, name in enumerate(ICON_NAMES):
            rect = pygame.Rect(index * 48, 0, 48, 48)
            icons[name] = self.sheet.subsurface(rect).copy()
        return icons

    def _star(self, surface, cx, cy, radius, color) -> None:
        points = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = radius if i % 2 == 0 else radius * 0.42
            points.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        pygame.draw.polygon(surface, color, points)

    def _triangle(self, surface, cx, cy, radius, color) -> None:
        points = []
        for i in range(3):
            ang = -math.pi / 2 + i * 2 * math.pi / 3
            points.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (90, 50, 10), points, 2)
        pygame.draw.line(surface, (90, 50, 10), (cx, cy - 6), (cx, cy + 3), 2)
        pygame.draw.circle(surface, (90, 50, 10), (cx, cy + 7), 1)

    def _icon_coin(self, sheet, cell) -> None:
        pygame.draw.circle(sheet, C["gold"], cell.center, 16)
        pygame.draw.circle(sheet, (210, 150, 20), cell.center, 16, 3)
        pygame.draw.circle(sheet, (255, 236, 140), cell.center, 8, 2)

    def _icon_flask(self, sheet, cell) -> None:
        cx, cy = cell.center
        pygame.draw.rect(sheet, (90, 180, 210), (cx - 5, cy - 16, 10, 12), border_radius=2)
        pygame.draw.polygon(sheet, (255, 255, 255), [(cx - 6, cy - 4), (cx + 6, cy - 4), (cx + 16, cy + 16), (cx - 16, cy + 16)])
        pygame.draw.polygon(sheet, C["ink"], [(cx - 6, cy - 4), (cx + 6, cy - 4), (cx + 16, cy + 16), (cx - 16, cy + 16)], 2)
        pygame.draw.rect(sheet, C["pink"], (cx - 12, cy + 6, 24, 10))

    def _icon_glitter(self, sheet, cell) -> None:
        pygame.draw.circle(sheet, (180, 90, 210), cell.center, 14)
        pygame.draw.circle(sheet, (255, 180, 230), cell.center, 8)
        self._star(sheet, cell.centerx - 10, cell.centery - 8, 5, C["gold"])
        self._star(sheet, cell.centerx + 12, cell.centery + 6, 4, C["white"])

    def _icon_star(self, sheet, cell) -> None:
        self._star(sheet, cell.centerx, cell.centery, 16, C["gold"])

    def _icon_seal(self, sheet, cell) -> None:
        pygame.draw.circle(sheet, (64, 150, 230), cell.center, 16)
        pygame.draw.circle(sheet, C["white"], cell.center, 16, 3)
        pygame.draw.circle(sheet, (190, 230, 255), cell.center, 7)

    def _icon_safety(self, sheet, cell) -> None:
        self._triangle(sheet, cell.centerx, cell.centery + 2, 18, (255, 186, 48))

    def _icon_lid(self, sheet, cell) -> None:
        pygame.draw.ellipse(sheet, (80, 90, 120), (cell.x + 6, cell.y + 16, 36, 16))
        pygame.draw.rect(sheet, (140, 150, 180), (cell.x + 14, cell.y + 10, 20, 12), border_radius=4)

    def _icon_drop(self, sheet, cell) -> None:
        cx, cy = cell.center
        pygame.draw.circle(sheet, (80, 170, 230), (cx, cy + 4), 10)
        pygame.draw.polygon(sheet, (80, 170, 230), [(cx, cy - 14), (cx - 9, cy + 2), (cx + 9, cy + 2)])
