"""
screens/base_screen.py — padre de las 5 estaciones + helpers de dibujo.

Para qué sirve:
    BaseScreen es lo que “conecta” cada interfaz con el resto del juego.
    Toda estación hereda de aquí y recibe la app (main.SlimeLab). Por eso
    self.state, self.physics y self.assets funcionan igual en ORDER o MIX.

    También hay funciones sueltas: blit (texto), panel, draw_reminder
    (cinta del pedido en BUILD/MIX/TOP).

Conectado con:
    - main.py importa blit, panel, draw_button, wrap_text
    - cada archivo de screens/*.py importa BaseScreen
    - draw_reminder lee state.order y settings.VISCOSITY_BANDS

Métodos que cada estación puede redefinir:
    handle_event  clics/teclas de ESA pantalla
    update(dt)    MIX y RESULT lo usan; las otras no
    draw          pintar
    on_enter      al cambiar de estación (BUILD sincroniza sliders)
"""

from __future__ import annotations

import math

import pygame

from settings import C, DECORATIONS, TIME_GRACE_S, TOP_BAR_H, VISCOSITY_BANDS, WIDTH


def blit(surface, font, msg, color, pos, anchor="topleft", shadow=None):
    if shadow:
        shade = font.render(msg, True, shadow)
        rect = shade.get_rect()
        setattr(rect, anchor, (pos[0] + 1, pos[1] + 1))
        surface.blit(shade, rect)
    image = font.render(msg, True, color)
    rect = image.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(image, rect)
    return rect


def panel(surface, rect, fill, border=None, radius=16, width=3):
    if len(fill) == 4 or (border is not None and len(border) == 4):
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, fill, layer.get_rect(), border_radius=radius)
        if border is not None:
            pygame.draw.rect(layer, border, layer.get_rect(), width, border_radius=radius)
        surface.blit(layer, rect.topleft)
        return
    shadow = rect.move(3, 4)
    pygame.draw.rect(surface, (40, 16, 60), shadow, border_radius=radius)
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border is not None:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)


def left_click(event, rect) -> bool:
    return (
        event.type == pygame.MOUSEBUTTONDOWN
        and getattr(event, "button", None) == 1
        and rect.collidepoint(event.pos)
    )


def draw_button(surface, rect, label, font, bg, mouse, enabled=True, fg=C["white"]):
    from ui_components import draw_candy_button

    draw_candy_button(surface, rect, bg, mouse, label=label, font=font, enabled=enabled)
    return enabled and rect.collidepoint(mouse)


def draw_star(surface, cx, cy, radius, color):
    points = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = radius if i % 2 == 0 else radius * 0.45
        points.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pygame.draw.polygon(surface, color, points)


def wrap_text(font, text, width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if font.size(trial)[0] <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_text(surface, font, text, color, pos, max_width, anchor="topleft", shadow=None):
    shown = text
    while shown and font.size(shown)[0] > max_width:
        shown = shown[:-2].rstrip() + "…"
        if shown == "…":
            break
    return blit(surface, font, shown, color, pos, anchor, shadow)


def draw_reference_card(surface, font, title: str) -> pygame.Rect:
    """Tarjeta blanca con encabezado rosa, del mismo tamaño que la del mockup."""
    rect = pygame.Rect(384, 54, 612, 470)
    pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=28)
    header = pygame.Rect(rect.x, rect.y, rect.w, 62)
    pink = (214, 58, 140)
    pygame.draw.rect(surface, pink, header, border_radius=28)
    pygame.draw.rect(surface, pink, (rect.x, header.bottom - 24, rect.w, 24))
    blit(surface, font, title, C["white"], header.center, "center")
    return rect


def draw_reminder(surface, font, order, service_time: float) -> None:
    """Barra superior con el pedido y el reloj. El reloj se pone naranja tras 120 s."""
    band = VISCOSITY_BANDS[order.viscosity]
    rect = pygame.Rect(16, TOP_BAR_H + 6, WIDTH - 32, 34)
    panel(surface, rect, (255, 255, 255, 230), None, radius=12)
    decos = ", ".join(DECORATIONS[key] for key in order.decorations)
    msg = (
        f"Pedido #{order.number}   ·   Slime {order.color_label}   ·   "
        f"Viscosidad {order.viscosity_label} ({band['low']:.1f}–{band['high']:.1f})   ·   {decos}"
    )
    prev = surface.get_clip()
    surface.set_clip(pygame.Rect(rect.x + 8, rect.y, rect.w - 70, rect.h))
    blit(surface, font, msg, C["ink"], (rect.x + 12, rect.centery), "midleft")
    surface.set_clip(prev)
    clock = f"{int(service_time) // 60}:{int(service_time) % 60:02d}"
    color = C["warn"] if service_time > TIME_GRACE_S else C["muted"]
    blit(surface, font, clock, color, (rect.right - 12, rect.centery), "midright")


class VSlider:
    """Slider vertical: arriba es el máximo, con lectura digital."""

    def __init__(self, center_x, y, height, min_v, max_v, value, lines, unit, accent, decimals):
        self.track = pygame.Rect(center_x - 11, y, 22, height)
        self.hit = pygame.Rect(center_x - 36, y - 4, 72, height + 8)
        self.min_v = min_v
        self.max_v = max_v
        self.value = value
        self.lines = lines
        self.unit = unit
        self.accent = accent
        self.decimals = decimals
        self.center_x = center_x

    def fraction(self) -> float:
        span = self.max_v - self.min_v
        if span <= 0:
            return 0.0
        return max(0.0, min(1.0, (self.value - self.min_v) / span))

    def set_from_y(self, mouse_y: int) -> None:
        span = max(1, self.track.h)
        t = 1.0 - (mouse_y - self.track.y) / span
        t = max(0.0, min(1.0, t))
        self.value = self.min_v + t * (self.max_v - self.min_v)

    def display(self) -> str:
        return f"{self.value:.{self.decimals}f}{self.unit}"

    def draw(self, surface, font, small) -> None:
        for index, line in enumerate(self.lines):
            if not line:
                continue
            blit(surface, small, line, C["white"], (self.center_x, self.track.y - 46 + index * 13), "midtop", C["shadow"])
        pygame.draw.rect(surface, (74, 52, 110), self.track, border_radius=10)
        handle_y = self.track.bottom - int(self.fraction() * self.track.h)
        fill = pygame.Rect(self.track.x, handle_y, self.track.w, self.track.bottom - handle_y)
        if fill.w > 2 and fill.h > 2:
            radius = min(10, fill.w // 2, fill.h // 2)
            pygame.draw.rect(surface, self.accent, fill, border_radius=radius)
        pygame.draw.circle(surface, C["white"], (self.track.centerx, handle_y), 13)
        pygame.draw.circle(surface, self.accent, (self.track.centerx, handle_y), 13, 3)
        pygame.draw.circle(surface, self.accent, (self.track.centerx, handle_y), 4)
        chip = pygame.Rect(self.center_x - 38, self.track.bottom + 8, 76, 24)
        pygame.draw.rect(surface, C["white"], chip, border_radius=8)
        blit(surface, font, self.display(), C["ink"], chip.center, "center")


def liquid_in_glass(surface, rect, color, fill, time, mixing=False) -> None:
    """Columna de líquido apoyada en el fondo del vaso del mockup."""
    fill = max(0.22, min(0.94, fill))
    liquid_h = max(18, int(rect.h * fill))
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    body = pygame.Rect(0, rect.h - liquid_h, rect.w, liquid_h)
    deep = (*tuple(max(0, int(channel * 0.72)) for channel in color), 145)
    mid = (*color, 120)
    light = (*tuple(min(255, int(channel * 0.55 + 120)) for channel in color), 170)
    radius = max(4, rect.w // 28)
    pygame.draw.rect(layer, deep, body, border_radius=radius)
    cap_h = max(8, rect.w // 8)
    wave = int((4 if mixing else 1) * math.sin(time * (4 if mixing else 2)))
    pygame.draw.ellipse(layer, light, (2, body.y - cap_h // 3 + wave, rect.w - 4, cap_h))
    pygame.draw.ellipse(layer, mid, (6, body.y + cap_h // 4 + wave, rect.w - 12, max(4, cap_h // 2)))
    for i in range(5 if mixing else 3):
        phase = (time * (1.5 if mixing else 0.7) + i * 0.19) % 1.0
        bx = 10 + int((i * 37) % max(1, rect.w - 18))
        by = rect.h - 10 - int(phase * max(8, liquid_h - 16))
        pygame.draw.circle(layer, (255, 255, 255, 120), (bx, by), 2 + (i % 2), 1)
    surface.blit(layer, rect.topleft)


class BaseScreen:
    """Plantilla. `app` es el SlimeLab de main.py (una sola instancia)."""

    def __init__(self, app) -> None:
        self.app = app

    @property
    def state(self):
        return self.app.state

    @property
    def assets(self):
        return self.app.assets

    @property
    def physics(self):
        return self.app.physics

    def handle_event(self, event) -> None:
        return None

    def update(self, dt: float) -> None:
        return None

    def draw(self, surface) -> None:
        return None

    def on_enter(self) -> None:
        return None
