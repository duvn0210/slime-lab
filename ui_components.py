"""Controles vectoriales de Slime Lab: tarjetas, botones, sliders, vaso y gráficas."""

from __future__ import annotations

import math

import pygame

from settings import C


def _tone(color, amount: float) -> tuple[int, int, int]:
    r, g, b = color[:3]
    if amount >= 0:
        return (
            min(255, int(r + (255 - r) * amount)),
            min(255, int(g + (255 - g) * amount)),
            min(255, int(b + (255 - b) * amount)),
        )
    t = 1.0 + amount
    return (max(0, int(r * t)), max(0, int(g * t)), max(0, int(b * t)))


def draw_candy_button(
    surface,
    rect,
    color,
    mouse,
    *,
    label="",
    font=None,
    subtitle="",
    sub_font=None,
    active=False,
    enabled=True,
    radius=None,
) -> pygame.Rect:
    """Botón tipo caramelito: borde grueso, labio 3D, brillo y texto con sombra."""
    hover = enabled and rect.collidepoint(mouse)
    body = pygame.Rect(rect)
    if active:
        body = body.move(0, -3)
    elif hover:
        body = body.move(0, -2)
    radius = body.h // 2 if radius is None else radius
    fill = color if enabled else (152, 156, 166)
    if hover and enabled:
        fill = _tone(fill, 0.16)
    lip = _tone(fill, -0.42)
    pygame.draw.rect(surface, (18, 8, 36), body.move(0, 5), border_radius=radius)
    pygame.draw.rect(surface, lip, body, border_radius=radius)
    face = pygame.Rect(body.x, body.y, body.w, max(14, int(body.h * 0.78)))
    pygame.draw.rect(surface, fill, face, border_radius=radius)
    inner = face.inflate(-6, -6)
    if inner.w > 8 and inner.h > 8:
        pygame.draw.rect(surface, _tone(fill, 0.42), inner, 2, border_radius=max(8, radius - 6))
    gloss = pygame.Surface(body.size, pygame.SRCALPHA)
    pygame.draw.ellipse(gloss, (255, 255, 255, 95), (8, 3, max(8, body.w - 16), max(8, body.h // 3)))
    surface.blit(gloss, body.topleft)
    outline = (255, 228, 80) if active else (32, 14, 52)
    pygame.draw.rect(surface, outline, body, 3, border_radius=radius)
    if font and label:
        cx, cy = body.centerx, body.centery - (7 if subtitle else 0)
        shade = font.render(label, True, (40, 12, 48))
        surface.blit(shade, shade.get_rect(center=(cx, cy + 1)))
        image = font.render(label, True, C["white"])
        surface.blit(image, image.get_rect(center=(cx, cy)))
    if sub_font and subtitle:
        sub = sub_font.render(subtitle, True, (255, 255, 255))
        surface.blit(sub, sub.get_rect(center=(body.centerx, body.centery + 11)))
    return body


def draw_card(surface, rect, fill=(255, 250, 252), radius=15, border=None, border_w=2) -> None:
    shadow = pygame.Surface((rect.w + 16, rect.h + 18), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (24, 10, 48, 72), shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, (rect.x - 4, rect.y + 6))
    if len(fill) == 4:
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, fill, layer.get_rect(), border_radius=radius)
        if border is not None:
            pygame.draw.rect(layer, border, layer.get_rect(), border_w, border_radius=radius)
        surface.blit(layer, rect.topleft)
        return
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border is not None:
        pygame.draw.rect(surface, border, rect, border_w, border_radius=radius)


class Card:
    def __init__(self, rect, fill=(255, 250, 252), radius=15, border=None) -> None:
        self.rect = pygame.Rect(rect)
        self.fill = fill
        self.radius = radius
        self.border = border

    def draw(self, surface) -> None:
        draw_card(surface, self.rect, self.fill, self.radius, self.border)


class Button:
    def __init__(self, rect, label: str, color) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color

    def hit(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def draw(self, surface, font, mouse, active=False, enabled=True) -> None:
        draw_candy_button(
            surface,
            self.rect,
            self.color,
            mouse,
            label=self.label,
            font=font,
            active=active,
            enabled=enabled,
        )


class CustomSlider:
    """Riel vertical: arriba es el máximo y la lectura va sobre el riel."""

    def __init__(self, center_x, top, height, min_v, max_v, value, title, unit, accent, decimals) -> None:
        self.track = pygame.Rect(center_x - 16, top, 32, height)
        self.hit = pygame.Rect(center_x - 42, top - 8, 84, height + 16)
        self.min_v = min_v
        self.max_v = max_v
        self.value = value
        self.title = title
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
        self.value = self.min_v + max(0.0, min(1.0, t)) * (self.max_v - self.min_v)

    def display(self) -> str:
        return f"{self.value:.{self.decimals}f}{self.unit}"

    def draw(self, surface, title_font, value_font) -> None:
        title = title_font.render(self.title, True, C["white"])
        surface.blit(title, title.get_rect(midbottom=(self.center_x, self.track.y - 46)))
        chip = pygame.Rect(self.center_x - 38, self.track.y - 40, 76, 28)
        pygame.draw.rect(surface, (20, 10, 36), chip.move(0, 2), border_radius=10)
        pygame.draw.rect(surface, C["white"], chip, border_radius=10)
        reading = value_font.render(self.display(), True, C["ink"])
        surface.blit(reading, reading.get_rect(center=chip.center))

        pygame.draw.rect(surface, (18, 12, 32), self.track.move(2, 3), border_radius=16)
        pygame.draw.rect(surface, (46, 32, 72), self.track, border_radius=16)
        pygame.draw.rect(surface, (210, 196, 230), self.track, 2, border_radius=16)
        handle_y = self.track.bottom - int(self.fraction() * (self.track.h - 8)) - 4
        fill = pygame.Rect(self.track.x + 4, handle_y, self.track.w - 8, self.track.bottom - handle_y - 4)
        if fill.h > 6:
            pygame.draw.rect(surface, self.accent, fill, border_radius=12)
        knob = (self.track.centerx, handle_y)
        pygame.draw.circle(surface, (30, 16, 48), (knob[0] + 1, knob[1] + 3), 18)
        pygame.draw.circle(surface, C["white"], knob, 16)
        pygame.draw.circle(surface, self.accent, knob, 16, 4)
        pygame.draw.circle(surface, self.accent, knob, 5)


Slider = CustomSlider


class ProgressBar:
    def __init__(self, rect) -> None:
        self.rect = pygame.Rect(rect)

    def draw(self, surface, ratio: float, font, label: str) -> None:
        ratio = max(0.0, min(1.0, ratio))
        caption = font.render(label, True, C["white"])
        surface.blit(caption, caption.get_rect(midbottom=(self.rect.centerx, self.rect.y - 6)))
        pygame.draw.rect(surface, (28, 18, 48), self.rect, border_radius=14)
        inner = self.rect.inflate(-6, -6)
        if ratio > 0:
            filled = pygame.Rect(inner.x, inner.y, max(12, int(inner.w * ratio)), inner.h)
            pygame.draw.rect(surface, (64, 196, 168), filled, border_radius=10)
        knob_x = inner.x + int(inner.w * ratio)
        pygame.draw.circle(surface, C["white"], (knob_x, inner.centery), inner.h // 2 + 4)
        pygame.draw.circle(surface, (40, 40, 56), (knob_x, inner.centery), inner.h // 2 + 4, 2)


class Beaker:
    """Vaso transparente con slime viscoso animado."""

    @staticmethod
    def draw(
        surface,
        rect,
        color,
        fill,
        time,
        *,
        mixing=False,
        angle=0.0,
        agitator=False,
        toppings=None,
        viscosity=2.5,
        rpm=80.0,
    ) -> pygame.Rect:
        toppings = toppings or set()
        glass = pygame.Rect(rect.x + 6, rect.y + 26, rect.w - 12, rect.h - 64)
        rim_h = 18
        rim = pygame.Rect(glass.x, glass.y - rim_h // 2, glass.w, rim_h)
        foot = pygame.Rect(glass.x + 22, rect.bottom - 16, glass.w - 44, 12)
        platform = pygame.Rect(glass.x - 2, foot.y - 16, glass.w + 4, 18)
        pygame.draw.rect(surface, (58, 64, 78), foot, border_radius=5)
        pygame.draw.rect(surface, (186, 194, 206), platform, border_radius=6)
        pygame.draw.rect(surface, (90, 98, 112), platform, 2, border_radius=6)

        pygame.draw.ellipse(surface, (158, 186, 214), rim)
        pygame.draw.ellipse(surface, (208, 226, 242), rim.inflate(-16, -8))

        inner = glass.inflate(-14, -12)
        fill = max(0.12, min(0.92, fill))
        liquid_h = max(22, int(inner.h * fill))
        body = pygame.Surface(glass.size, pygame.SRCALPHA)
        jar = body.get_rect()
        radii = {"border_top_left_radius": 0, "border_top_right_radius": 0, "border_bottom_left_radius": 34, "border_bottom_right_radius": 34}
        pygame.draw.rect(body, (255, 255, 255, 34), jar, **radii)
        local = pygame.Rect(inner.x - glass.x, inner.bottom - glass.y - liquid_h, inner.w, liquid_h)
        slime = pygame.Surface(glass.size, pygame.SRCALPHA)
        _draw_slime(slime, local, color, time, mixing, angle, viscosity, rpm, toppings)
        mask = pygame.Surface(glass.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect().inflate(-6, 0), **radii)
        slime.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        body.blit(slime, (0, 0))
        pygame.draw.line(body, (236, 246, 255, 240), (2, 0), (2, jar.h - 34), 4)
        pygame.draw.line(body, (200, 216, 232, 220), (jar.w - 3, 0), (jar.w - 3, jar.h - 34), 4)
        pygame.draw.arc(body, (236, 246, 255, 240), pygame.Rect(2, jar.h - 68, jar.w - 4, 66), math.pi, math.tau, 4)
        pygame.draw.line(body, (255, 255, 255, 210), (16, 6), (16, jar.h - 40), 4)
        surface.blit(body, glass.topleft)

        for mark in range(1, 6):
            my = inner.bottom - int(inner.h * mark / 5)
            pygame.draw.line(surface, (70, 82, 108), (inner.right - 16, my), (inner.right - 4, my), 2)

        pygame.draw.arc(surface, (252, 254, 255), rim.inflate(2, 2), 0.04, math.pi - 0.04, 7)
        pygame.draw.arc(surface, (120, 148, 176), rim, 0.0, math.pi, 2)

        if "lid" in toppings:
            _draw_lid(surface, glass)
        elif agitator:
            _agitator(surface, glass, inner.bottom - liquid_h, angle, mixing)
        _draw_flask_stickers(surface, glass, time, toppings)
        return glass


def _draw_slime(body, liquid, color, time, mixing, angle, viscosity, rpm, toppings) -> None:
    mu = max(0.3, float(viscosity))
    thick = min(1.0, mu / 8.0)
    thin = 1.0 - thick
    mix = 1.0 if mixing else 0.0
    speed = (0.42 + thin * 2.05) * (0.75 + mix * 1.15) * (0.45 + rpm / 220.0)
    amp = (10 + 22 * thin) * (0.85 + mix * 1.35)
    shear = (6 + 22 * thin) * (0.35 + mix * 1.1) * math.sin(angle if mixing else time * speed)
    deep = (*tuple(max(0, int(ch * 0.68)) for ch in color), 240)
    mid = (*color, 228)
    light = (*tuple(min(255, int(ch * 0.5 + 120)) for ch in color), 235)
    highlight = (*tuple(min(255, ch + 80) for ch in color), 150)

    left = liquid.x + 3.0
    right = liquid.right - 3.0
    bottom = liquid.bottom - 1.0
    base_top = liquid.y + 10.0
    width = max(8.0, right - left)
    height = max(12.0, bottom - base_top)
    steps = 28
    surface_pts = []
    for i in range(steps + 1):
        t = i / steps
        x = left + width * t + shear * math.sin(t * math.pi) * 0.35
        envelope = 0.35 + 0.65 * math.sin(t * math.pi)
        y = (
            base_top
            + math.sin(time * speed * 1.7 + t * 5.8) * amp * envelope
            + math.sin(time * speed * 0.85 + t * 11.4) * amp * 0.42
            + math.sin(time * speed * 3.1 + t * 2.6) * amp * (0.18 + 0.28 * mix)
        )
        if mixing:
            y += math.sin(angle * 1.6 + t * math.tau) * amp * 0.7
            x += math.cos(angle + t * math.tau) * (4 + 10 * thin)
        surface_pts.append((x, y))

    radius = min(18.0, width * 0.18)
    blob = []
    for i in range(7):
        a = math.pi + i * (math.pi / 12)
        blob.append((left + radius + math.cos(a) * radius, bottom + math.sin(a) * radius * 0.35))
    blob.append((left + math.sin(time * speed * 0.7) * (3 + 7 * thick), (base_top + bottom) * 0.55))
    blob.extend(surface_pts)
    blob.append((right + math.sin(time * speed * 0.7 + 1.4) * (3 + 7 * thick), (base_top + bottom) * 0.55))
    for i in range(7):
        a = -math.pi / 12 + i * (math.pi / 12)
        blob.append((right - radius + math.cos(a) * radius, bottom + math.sin(a) * radius * 0.35))
    pygame.draw.polygon(body, deep, blob)

    inset = []
    cx = (left + right) / 2 + shear * 0.25
    cy = (base_top + bottom) / 2
    for x, y in blob:
        inset.append((x + (cx - x) * 0.16, y + (cy - y) * 0.1))
    pygame.draw.polygon(body, mid, inset)

    fold = []
    for i, (x, y) in enumerate(surface_pts):
        t = i / steps
        fy = y + 10 + math.sin(time * speed + t * 8) * (4 + 8 * thin)
        fold.append((x, fy))
    fold.append((right - 8, bottom - 10))
    fold.append((left + 8, bottom - 10))
    pygame.draw.polygon(body, highlight, fold)

    pygame.draw.lines(body, light, False, [(x, y + 1) for x, y in surface_pts], max(4, int(8 * thick + 2)))

    n_bubbles = 6 + int(10 * thin) + int(mix * 6)
    for i in range(n_bubbles):
        rise = (0.18 + thin * 0.55) * (1.0 + mix * 1.4)
        phase = (time * rise + i * 0.17) % 1.0
        wobble = math.sin(time * speed + i) * (6 + 10 * thin)
        bx = int(left + 12 + ((i * 0.19) % 1.0) * (width - 24) + wobble)
        by = int(bottom - 10 - phase * max(14, height - 16))
        pygame.draw.circle(body, (255, 255, 255, 80 + int(90 * thin)), (bx, by), 2 + (i % 3), 1)

    if mixing:
        vortex_x = cx + math.cos(angle) * (10 + 8 * thin)
        vortex_y = cy + math.sin(angle * 0.8) * (8 + 6 * thin)
        for k in range(4):
            swirl = pygame.Rect(
                vortex_x - 22 - k * 8,
                vortex_y - 14 - k * 6,
                44 + k * 16,
                28 + k * 12,
            )
            pygame.draw.arc(body, highlight, swirl, angle + k * 0.8, angle + k * 0.8 + 1.7, 3)
        peak_x = vortex_x
        peak_y = min(p[1] for p in surface_pts) - 4 - 12 * thin
        pygame.draw.ellipse(body, light, (peak_x - 14, peak_y, 28, 18 + 10 * thin))

    crawl = time * (0.28 + thin * 1.15)
    for i in range(4):
        gx = left + 10 + (math.sin(crawl + i * 1.7) * 0.5 + 0.5) * max(10, width - 40)
        gy = base_top + 14 + (math.cos(crawl * 0.65 + i * 1.3) * 0.5 + 0.5) * max(10, height * 0.5)
        pygame.draw.ellipse(body, highlight, (gx, gy, 20 + 10 * thick, 9 + 6 * thick))

    if "glitter" in toppings:
        palette = (
            (255, 255, 255, 240),
            (255, 220, 80, 240),
            (255, 120, 200, 230),
            (120, 230, 255, 230),
            (255, 160, 80, 230),
        )
        for i in range(36):
            gx = left + 6 + (i * 47 + time * (30 + 55 * thin)) % max(1, width - 12)
            gy = base_top + 6 + (i * 23 + math.sin(time * 1.4 + i) * 8) % max(1, height - 12)
            twinkle = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(time * 9 + i * 0.7))
            _sparkle(body, gx, gy, 2.2 + (i % 4) * twinkle, palette[i % len(palette)])
    if "stars" in toppings:
        colors = (
            (255, 214, 64),
            (255, 110, 180),
            (90, 210, 255),
            (170, 120, 255),
            (255, 150, 70),
            (120, 240, 160),
        )
        layout = (
            (0.22, 0.28, 11),
            (0.68, 0.38, 9),
            (0.42, 0.58, 13),
            (0.78, 0.68, 8),
            (0.30, 0.78, 10),
            (0.55, 0.22, 7),
        )
        for i, (fx, fy, rad) in enumerate(layout):
            sx = left + width * fx
            sy = base_top + height * fy + math.sin(time * (1.4 + thin) + i) * 6
            spin = time * (0.6 + 0.2 * i)
            pulse = rad * (0.88 + 0.12 * math.sin(time * 4 + i))
            _star(body, sx, sy, pulse, (*colors[i], 255), spin=spin, outline=(40, 16, 56, 255))


def draw_chart(surface, rect, title, series, x_max, y_max, color, assets, band=None, dashed=None) -> None:
    draw_card(surface, rect, C["white"], 15, (220, 210, 230))
    title_img = assets.md.render(title, True, C["ink"])
    surface.blit(title_img, (rect.x + 16, rect.y + 12))
    plot = pygame.Rect(rect.x + 46, rect.y + 48, rect.w - 64, rect.h - 72)
    pygame.draw.rect(surface, (246, 248, 252), plot, border_radius=8)
    pygame.draw.rect(surface, (180, 176, 196), plot, 1, border_radius=8)
    x_max = max(float(x_max), 0.001)
    y_max = max(float(y_max), 0.001)
    if band is not None:
        low, high = band
        y0 = plot.bottom - int(plot.h * max(0.0, min(1.0, low / y_max)))
        y1 = plot.bottom - int(plot.h * max(0.0, min(1.0, high / y_max)))
        band_rect = pygame.Rect(plot.x + 1, min(y0, y1), plot.w - 2, abs(y1 - y0) or 2)
        layer = pygame.Surface(band_rect.size, pygame.SRCALPHA)
        layer.fill((76, 175, 80, 70))
        surface.blit(layer, band_rect.topleft)
    if dashed is not None:
        y = plot.bottom - int(plot.h * max(0.0, min(1.0, dashed / y_max)))
        for x in range(plot.x + 4, plot.right - 4, 10):
            pygame.draw.line(surface, (120, 90, 160), (x, y), (x + 5, y), 2)
    points = []
    for x_val, y_val in series:
        px = plot.x + int(plot.w * max(0.0, min(1.0, x_val / x_max)))
        py = plot.bottom - int(plot.h * max(0.0, min(1.0, y_val / y_max)))
        points.append((px, py))
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 3)
    axis = assets.tiny.render("0", True, C["muted"])
    surface.blit(axis, (plot.x - 16, plot.bottom - 8))


def _star(surface, cx, cy, radius, color, spin=0.0, outline=None) -> None:
    points = []
    for i in range(10):
        ang = -math.pi / 2 + spin + i * math.pi / 5
        rad = radius if i % 2 == 0 else radius * 0.42
        points.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    if outline is not None:
        pygame.draw.polygon(surface, outline, points)
        inner = []
        for i in range(10):
            ang = -math.pi / 2 + spin + i * math.pi / 5
            rad = (radius * 0.82) if i % 2 == 0 else radius * 0.34
            inner.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        pygame.draw.polygon(surface, color, inner)
    else:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.circle(surface, (255, 255, 255, 180), (int(cx - radius * 0.15), int(cy - radius * 0.18)), max(1, int(radius * 0.18)))


def _sparkle(surface, x, y, size, color) -> None:
    cx, cy = int(x), int(y)
    span = max(2, int(size * 2.4))
    pygame.draw.line(surface, color, (cx - span, cy), (cx + span, cy), 2)
    pygame.draw.line(surface, color, (cx, cy - span), (cx, cy + span), 2)
    diag = max(1, int(span * 0.6))
    pygame.draw.line(surface, color, (cx - diag, cy - diag), (cx + diag, cy + diag), 1)
    pygame.draw.circle(surface, color, (cx, cy), max(1, int(size)))


def _draw_lid(surface, glass) -> None:
    cap = pygame.Rect(glass.x - 4, glass.y - 16, glass.w + 8, 22)
    pygame.draw.ellipse(surface, (48, 28, 72), cap.move(0, 3))
    pygame.draw.ellipse(surface, (255, 92, 156), cap)
    pygame.draw.ellipse(surface, (255, 176, 210), pygame.Rect(cap.x + 14, cap.y + 4, cap.w - 28, 8))
    pygame.draw.ellipse(surface, (90, 30, 70), cap, 2)
    knob = (glass.centerx, glass.y - 20)
    pygame.draw.circle(surface, (255, 210, 70), knob, 8)
    pygame.draw.circle(surface, (255, 255, 220), (knob[0] - 2, knob[1] - 2), 3)
    pygame.draw.circle(surface, (140, 90, 20), knob, 8, 2)


def _draw_flask_stickers(surface, glass, time, toppings) -> None:
    if "safety" in toppings:
        sticker = pygame.Surface((72, 86), pygame.SRCALPHA)
        pygame.draw.rect(sticker, (40, 18, 12, 90), (4, 8, 62, 74), border_radius=10)
        pygame.draw.rect(sticker, (255, 214, 48), (2, 4, 62, 74), border_radius=10)
        pygame.draw.rect(sticker, (48, 28, 20), (2, 4, 62, 74), 3, border_radius=10)
        for i in range(5):
            y = 10 + i * 12
            pygame.draw.rect(sticker, (32, 24, 24), (8, y, 50, 6), border_radius=2)
        pygame.draw.polygon(sticker, (255, 248, 210), ((34, 16), (56, 58), (12, 58)))
        pygame.draw.polygon(sticker, (28, 20, 18), ((34, 16), (56, 58), (12, 58)), 3)
        pygame.draw.rect(sticker, (28, 20, 18), (31, 30, 6, 16), border_radius=2)
        pygame.draw.circle(sticker, (28, 20, 18), (34, 52), 4)
        pygame.draw.polygon(sticker, (255, 255, 255, 160), ((8, 10), (22, 8), (10, 22)))
        tilted = pygame.transform.rotate(sticker, -11)
        surface.blit(tilted, tilted.get_rect(center=(glass.x + 58, glass.y + glass.h * 0.44)))
    if "seal" in toppings:
        cx = glass.right - 42
        cy = glass.bottom - 78
        ribbon = ((cx - 10, cy + 10), (cx - 22, cy + 38), (cx - 2, cy + 24))
        ribbon_r = ((cx + 10, cy + 10), (cx + 22, cy + 38), (cx + 2, cy + 24))
        pygame.draw.polygon(surface, (210, 48, 88), ribbon)
        pygame.draw.polygon(surface, (255, 92, 130), ribbon_r)
        pygame.draw.circle(surface, (40, 20, 16), (cx + 2, cy + 3), 26)
        pygame.draw.circle(surface, (255, 196, 64), (cx, cy), 26)
        pygame.draw.circle(surface, (255, 230, 140), (cx, cy), 20)
        pygame.draw.circle(surface, (196, 120, 24), (cx, cy), 20, 2)
        pygame.draw.circle(surface, (255, 92, 130), (cx, cy), 14)
        _star(surface, cx, cy, 9, (255, 240, 160), spin=time * 0.4, outline=(120, 40, 40))
        pygame.draw.circle(surface, (255, 255, 255), (cx - 7, cy - 8), 4)


def _agitator(surface, glass, liquid_top, angle, mixing) -> None:
    cx = glass.centerx
    housing = pygame.Rect(cx - 34, glass.y - 48, 68, 38)
    pygame.draw.rect(surface, (36, 28, 48), housing.move(0, 4), border_radius=14)
    pygame.draw.rect(surface, (255, 146, 64) if mixing else (168, 176, 192), housing, border_radius=14)
    face = housing.inflate(-10, -14)
    face.y = housing.y + 6
    pygame.draw.rect(surface, (255, 210, 150) if mixing else (220, 226, 236), face, border_radius=10)
    for i in range(3):
        slot = pygame.Rect(housing.x + 12 + i * 14, housing.y + 8, 8, 6)
        pygame.draw.rect(surface, (90, 64, 40) if mixing else (140, 148, 160), slot, border_radius=2)
    led = (housing.right - 14, housing.centery)
    pygame.draw.circle(surface, (80, 255, 140) if mixing else (120, 128, 140), led, 5)
    pygame.draw.circle(surface, (220, 255, 230) if mixing else (200, 204, 210), (led[0] - 1, led[1] - 1), 2)
    pygame.draw.rect(surface, (70, 78, 96), (cx - 16, housing.bottom - 6, 32, 12), border_radius=4)
    chuck = pygame.Rect(cx - 9, housing.bottom + 4, 18, 12)
    pygame.draw.rect(surface, (210, 218, 230), chuck, border_radius=3)
    pygame.draw.rect(surface, (90, 98, 112), chuck, 2, border_radius=3)
    clamp = pygame.Rect(cx - 18, glass.y - 7, 36, 10)
    pygame.draw.rect(surface, (92, 102, 122), clamp, border_radius=3)
    pygame.draw.rect(surface, (220, 228, 240), clamp.inflate(-18, -4), border_radius=2)

    hub_y = min(max(liquid_top + 28, glass.y + 70), glass.bottom - 48)
    pygame.draw.line(surface, (118, 128, 148), (cx + 2, chuck.bottom), (cx + 2, hub_y), 6)
    pygame.draw.line(surface, (232, 238, 246), (cx, chuck.bottom), (cx, hub_y), 5)
    pygame.draw.line(surface, (255, 255, 255), (cx - 1, chuck.bottom + 4), (cx - 1, hub_y - 4), 2)

    blades = []
    for i in range(3):
        a = angle + i * math.tau / 3
        blades.append((math.sin(a), math.cos(a) * 40, math.sin(a) * 13, a))
    for depth, dx, dy, a in sorted(blades):
        pw, ph = 34, 13
        paddle = pygame.Rect(0, 0, pw, ph)
        paddle.center = (cx + dx, hub_y + dy)
        fill = (255, 214, 96) if mixing else (186, 196, 210)
        if depth < 0:
            fill = tuple(max(0, c - 40) for c in fill)
        pygame.draw.ellipse(surface, fill, paddle)
        pygame.draw.ellipse(surface, (90, 70, 40) if mixing else (70, 80, 96), paddle, 2)
    pygame.draw.circle(surface, (255, 196, 64) if mixing else (200, 208, 220), (cx, hub_y), 9)
    pygame.draw.circle(surface, (90, 70, 30) if mixing else (80, 88, 104), (cx, hub_y), 9, 2)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, hub_y - 2), 3)
