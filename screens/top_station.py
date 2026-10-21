"""
Cuarta pantalla: decoras el vaso y lo entregas.

Clic en un adorno = lo pones o lo quitas.
Si lo arrastras hasta el vaso, también se pone.
Las herramientas que el cliente pidió dicen “pedido” en la esquina.

Para entregar tienes que haber hecho los tres pasos de antes:
  1. Confirmar la receta en BUILD
  2. Detener la mezcla en MIX
  3. Haber elegido un colorante
Si falta uno, sale un avisito amarillo y no entrega.

Al entregar se calcula la nota (en physics_engine) y pasas a la última hoja.
"""

from __future__ import annotations

import math

import pygame

from settings import BOTTOM_BAR_H, C, DECORATIONS, DYES, HEIGHT, TOP_BAR_H
from screens.base_screen import BaseScreen, blit, draw_reminder, wrap_text
from ui_components import Beaker, Button, draw_card


TOOL_ICON = {
    "glitter": "glitter",
    "safety": "safety",
    "seal": "seal",
    "stars": "star",
    "lid": "lid",
}


class TopStation(BaseScreen):
    def __init__(self, app) -> None:
        """Coloca las 5 herramientas, el vaso y el botón Entregar Pedido."""
        super().__init__(app)
        left = ("safety", "seal", "glitter")
        right = ("stars", "lid")
        self.tools = {}
        y = TOP_BAR_H + 70
        for key in left:
            self.tools[key] = pygame.Rect(16, y, 210, 56)
            y += 64
        y = TOP_BAR_H + 70
        for key in right:
            self.tools[key] = pygame.Rect(760, y, 240, 56)
            y += 64
        self.beaker = pygame.Rect(360, TOP_BAR_H + 56, 220, HEIGHT - BOTTOM_BAR_H - TOP_BAR_H - 120)
        self.deliver = Button(
            pygame.Rect(380, HEIGHT - BOTTOM_BAR_H - 48, 180, 40),
            "Entregar Pedido",
            C["green"],
        )
        self.drag = None
        self.drag_pos = (0, 0)
        self.drag_moved = False

    def handle_event(self, event) -> None:
        """Clic = poner/quitar adorno. Arrastrar al vaso = ponerlo. Entregar pide la nota."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.tools.items():
                if rect.collidepoint(event.pos):
                    self.drag = key
                    self.drag_pos = event.pos
                    self.drag_moved = False
                    return
            if self.deliver.hit(event.pos):
                self._deliver()
        elif event.type == pygame.MOUSEMOTION and self.drag is not None:
            if math.hypot(event.pos[0] - self.drag_pos[0], event.pos[1] - self.drag_pos[1]) > 6:
                self.drag_moved = True
            self.drag_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag is not None:
            key = self.drag
            if self.drag_moved:
                if self.beaker.collidepoint(event.pos):
                    self.state.applied.add(key)
            else:
                self.state.toggle_decoration(key)
            self.drag = None

    def _deliver(self) -> None:
        """Revisa que no falte nada, pide la nota y cambia a la pantalla de control de calidad."""
        if not self.state.recipe.confirmed:
            self.app.notify("Confirma la formulación en BUILD.")
            return
        if not self.state.mix_locked:
            self.app.notify("Detén la mezcla para fijar la viscosidad.")
            return
        if not self.state.recipe.color:
            self.app.notify("Elige un colorante en la estación de formulación.")
            return
        self.state.deliver(self.physics)
        self.app.current = "result"
        self.app.screens["result"].on_enter()

    def draw(self, surface) -> None:
        """Pinta herramientas, vaso con stickers y el botón verde de entregar."""
        self.assets.blit_background(surface)
        draw_reminder(surface, self.assets.sm, self.state.order, self.state.service_time)
        for key, rect in self.tools.items():
            self._draw_tool(surface, key, rect)
        recipe = self.state.recipe
        liquid = DYES.get(recipe.color, (214, 176, 214))
        fill = self.physics.nivel_visual(recipe.polymer, recipe.agent)
        eq = self.physics.estado_reologico(recipe.polymer, recipe.agent, recipe.rpm)
        mu = self.state.achieved_mu if self.state.achieved_mu is not None else eq["mu"]
        Beaker.draw(
            surface,
            self.beaker,
            liquid,
            fill,
            self.app.time,
            toppings=self.state.applied,
            agitator=False,
            viscosity=mu,
            rpm=recipe.rpm,
        )
        self.deliver.draw(surface, self.assets.md, self.app.mouse)
        if self.drag and self.drag_moved:
            icon = pygame.transform.smoothscale(self.assets.icons[TOOL_ICON[self.drag]], (48, 48))
            surface.blit(icon, (self.drag_pos[0] - 24, self.drag_pos[1] - 24))

    def _draw_tool(self, surface, key, rect) -> None:
        """Una herramienta. Si el cliente la pidió y no está, dice 'pedido'."""
        applied = key in self.state.applied
        needed = key in self.state.order.decorations
        fill = (232, 255, 236) if applied else C["white"]
        border = C["good"] if applied else (C["gold"] if needed else (190, 180, 200))
        draw_card(surface, rect, fill, 15, border, 3 if needed or applied else 2)
        icon = pygame.transform.smoothscale(self.assets.icons[TOOL_ICON[key]], (40, 40))
        surface.blit(icon, (rect.x + 14, rect.centery - 20))
        lines = wrap_text(self.assets.sm, DECORATIONS[key], rect.w - 80)[:2]
        top = rect.centery - (len(lines) - 1) * 10
        for index, line in enumerate(lines):
            blit(surface, self.assets.sm, line, C["ink"], (rect.x + 64, top + index * 20), "midleft")
        if needed and not applied:
            blit(surface, self.assets.tiny, "pedido", C["pink_deep"], (rect.right - 12, rect.y + 8), "topright")
