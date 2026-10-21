"""Estación 5: reporte de control de calidad."""

from __future__ import annotations

import random

import pygame

from settings import BOTTOM_BAR_H, C, DYES, GRADE_EXCELLENT, GRADE_GOOD, HEIGHT, WIDTH
from screens.base_screen import BaseScreen, blit, fit_text
from ui_components import Button, draw_card


class ResultStation(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.card = pygame.Rect(318, 58, 430, 338)
        self.next = Button(pygame.Rect(368, 412, 330, 44), "Nuevo Pedido", C["green"])
        self.bits: list[dict] = []
        self.shown_coins = 0.0

    def on_enter(self) -> None:
        self.shown_coins = 0.0
        self.bits = []
        report = self.state.last_report
        if not report or report["total"] < GRADE_EXCELLENT:
            return
        rng = random.Random(self.state.order.number * 17 + report["total"])
        palette = (C["gold"], C["pink"], C["white"], C["blue"], (120, 230, 160))
        for _ in range(48):
            self.bits.append(
                {
                    "x": rng.uniform(20, WIDTH - 20),
                    "y": rng.uniform(-160, -8),
                    "vx": rng.uniform(-40, 40),
                    "vy": rng.uniform(80, 200),
                    "w": rng.randint(5, 9),
                    "h": rng.randint(8, 14),
                    "color": rng.choice(palette),
                }
            )

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.next.hit(event.pos):
            self.app.next_order()

    def update(self, dt: float) -> None:
        report = self.state.last_report
        if report:
            self.shown_coins = min(report["monedas"], self.shown_coins + max(1.0, report["monedas"] * dt * 1.8))
        for bit in self.bits:
            bit["y"] += bit["vy"] * dt
            bit["x"] += bit["vx"] * dt
            if bit["y"] > HEIGHT - BOTTOM_BAR_H:
                bit["y"] = -12
                bit["x"] = max(10, min(WIDTH - 10, bit["x"]))

    def draw(self, surface) -> None:
        self.assets.blit_background(surface)
        order = self.state.order
        report = self.state.last_report
        mood = "ok"
        if report:
            if report["total"] >= GRADE_EXCELLENT:
                mood = "happy"
            elif report["total"] < GRADE_GOOD:
                mood = "sad"
        self.assets.draw_customer(surface, order, mood=mood)
        for bit in self.bits:
            pygame.draw.rect(surface, bit["color"], (bit["x"], bit["y"], bit["w"], bit["h"]))
        self._draw_ticket(surface, report)
        self.next.draw(surface, self.assets.md, self.app.mouse)

    def _draw_ticket(self, surface, report) -> None:
        card = self.card
        draw_card(surface, card, (255, 252, 255), 22, (232, 196, 214), 3)
        header = pygame.Rect(card.x, card.y, card.w, 52)
        pygame.draw.rect(surface, (236, 78, 154), header, border_top_left_radius=22, border_top_right_radius=22)
        pygame.draw.rect(surface, (236, 78, 154), (header.x, header.bottom - 16, header.w, 16))
        blit(surface, self.assets.lg, "Control de calidad", C["white"], (card.x + 22, header.centery), "midleft")
        if report is None:
            blit(surface, self.assets.md, "Todavía no hay un pedido entregado.", C["muted"], card.center, "center")
            return
        order = self.state.order
        dye = DYES.get(order.color, C["pink"])
        rows = (
            (self.assets.icons["flask"], f"Color {report['color']} / 50", dye, True),
            (self.assets.icons["drop"], f"Viscosidad {report['viscosidad']} / 50", (70, 150, 210), False),
            (self.assets.icons["glitter"], f"Decoración {report['decoracion']} / 10", (176, 92, 214), True),
        )
        y = card.y + 62
        inner_w = card.w - 28
        for icon, text, accent, striped in rows:
            row = pygame.Rect(card.x + 14, y, inner_w, 46)
            fill = (255, 228, 238) if striped else (248, 246, 252)
            pygame.draw.rect(surface, fill, row, border_radius=12)
            pygame.draw.circle(surface, accent, (row.x + 26, row.centery), 16)
            pygame.draw.circle(surface, C["white"], (row.x + 26, row.centery), 16, 2)
            surface.blit(pygame.transform.smoothscale(icon, (20, 20)), (row.x + 16, row.centery - 10))
            fit_text(surface, self.assets.md, text, (42, 28, 64), (row.x + 52, row.centery), row.w - 66, "midleft")
            y += 52
        ink = (34, 34, 34)
        blit(surface, self.assets.xl, f"{report['total']} / 100", ink, (card.centerx, y + 8), "center")
        grade_color = C["good"] if report["total"] >= 70 else C["warn"]
        blit(surface, self.assets.lg, report["calificacion"], grade_color, (card.centerx, y + 42), "center")
        blit(
            surface,
            self.assets.md,
            f"+{int(self.shown_coins)} monedas",
            (212, 156, 32),
            (card.centerx, y + 72),
            "center",
        )
