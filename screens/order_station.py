# AI assisted development
"""Estación 1: el cliente entrega el pedido."""

from __future__ import annotations

import pygame

from settings import C, DYES, VISCOSITY_BANDS
from screens.base_screen import BaseScreen, blit, fit_text
from ui_components import Button, draw_card


class OrderStation(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.card = pygame.Rect(318, 58, 430, 268)
        self.manual = Button(pygame.Rect(368, 338, 330, 44), "Manual de Fórmulas", (46, 132, 214))

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.manual.hit(event.pos):
            self.app.manual = True

    def draw(self, surface) -> None:
        self.assets.blit_background(surface)
        order = self.state.order
        self.assets.draw_customer(surface, order, mood="ok")
        self._draw_ticket(surface, order)
        self.manual.draw(surface, self.assets.md, self.app.mouse)

    def _draw_ticket(self, surface, order) -> None:
        card = self.card
        draw_card(surface, card, (255, 252, 255), 22, (232, 196, 214), 3)
        header = pygame.Rect(card.x, card.y, card.w, 52)
        pygame.draw.rect(surface, (236, 78, 154), header, border_top_left_radius=22, border_top_right_radius=22)
        pygame.draw.rect(surface, (236, 78, 154), (header.x, header.bottom - 16, header.w, 16))
        blit(surface, self.assets.lg, f"Pedido #{order.number}", C["white"], (card.x + 22, header.centery), "midleft")
        band = VISCOSITY_BANDS[order.viscosity]
        rows = (
            (self.assets.icons["flask"], f"{order.color_label} Slime", DYES.get(order.color, C["pink"]), True),
            (self.assets.icons["drop"], f"Viscosidad {order.viscosity_label}", (70, 150, 210), False),
            (self.assets.icons["glitter"], order.decoration_label, (176, 92, 214), True),
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
        note = f"Banda {band['low']:.1f}–{band['high']:.1f} Pa·s"
        pill = pygame.Rect(card.x + 18, card.bottom - 36, card.w - 36, 22)
        pygame.draw.rect(surface, (244, 232, 248), pill, border_radius=11)
        blit(surface, self.assets.tiny, note, (120, 70, 140), pill.center, "center")
        chevron = [
            (card.centerx - 10, card.bottom - 2),
            (card.centerx + 10, card.bottom - 2),
            (card.centerx, card.bottom + 10),
        ]
        pygame.draw.polygon(surface, (255, 252, 255), chevron)
        pygame.draw.polygon(surface, (232, 196, 214), chevron, 2)
