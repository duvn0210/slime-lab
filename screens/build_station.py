"""
screens/build_station.py — estación BUILD (formulación).

Para qué sirve:
    Tres sliders (polímero, agente [A], RPM) y la paleta de colorante.
    Cada movimiento llama state.update_recipe. Confirmar pone confirmed=True
    para que MIX pueda girar. Si después mueves un slider, se borra MIX.

Conectado con:
    - game_state.update_recipe / set_color / confirm
    - physics.nivel_visual y estado_reologico (solo para el vaso)
    - ui_components.CustomSlider y Beaker
    - settings  rangos POLYMER_*, AGENT_*, RPM_*
"""

from __future__ import annotations

import pygame

from settings import (
    AGENT_MAX,
    AGENT_MIN,
    BOTTOM_BAR_H,
    C,
    COLOR_LABELS,
    DYES,
    HEIGHT,
    POLYMER_MAX,
    POLYMER_MIN,
    RPM_MAX,
    RPM_MIN,
    TOP_BAR_H,
)
from screens.base_screen import BaseScreen, blit, draw_reminder
from ui_components import Beaker, Button, CustomSlider, draw_candy_button


class BuildStation(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        recipe = self.state.recipe
        track_top = TOP_BAR_H + 112
        track_h = HEIGHT - BOTTOM_BAR_H - track_top - 10
        specs = (
            ("polymer", 70, recipe.polymer, "Polímero", " %", C["pink"], 1, POLYMER_MIN, POLYMER_MAX),
            ("agent", 175, recipe.agent, "Agente", " M", (156, 39, 176), 2, AGENT_MIN, AGENT_MAX),
            ("rpm", 280, recipe.rpm, "Velocidad", " RPM", C["blue"], 0, RPM_MIN, RPM_MAX),
        )
        self.sliders = []
        self.slider_by_key = {}
        for key, cx, value, title, unit, accent, decimals, min_v, max_v in specs:
            slider = CustomSlider(cx, track_top, track_h, min_v, max_v, value, title, unit, accent, decimals)
            self.sliders.append(slider)
            self.slider_by_key[key] = slider
        self.active = None
        self.beaker = pygame.Rect(360, TOP_BAR_H + 78, 190, HEIGHT - BOTTOM_BAR_H - TOP_BAR_H - 140)
        self.confirm = Button(
            pygame.Rect(320, HEIGHT - BOTTOM_BAR_H - 46, 240, 40),
            "Confirmar Formulación",
            C["purple"],
        )
        self.color_rects = {}
        x = 620
        y = TOP_BAR_H + 88
        for key in ("rosa", "verde", "azul", "naranja", "morado", "amarillo"):
            self.color_rects[key] = pygame.Rect(x, y, 200, 40)
            y += 48

    def on_enter(self) -> None:
        recipe = self.state.recipe
        self.slider_by_key["polymer"].value = recipe.polymer
        self.slider_by_key["agent"].value = recipe.agent
        self.slider_by_key["rpm"].value = recipe.rpm

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slider in self.sliders:
                if slider.hit.collidepoint(event.pos):
                    self.active = slider
                    slider.set_from_y(event.pos[1])
                    self._push()
                    return
            for key, rect in self.color_rects.items():
                if rect.collidepoint(event.pos):
                    self.state.set_color(key)
                    return
            if self.confirm.hit(event.pos):
                self.state.confirm()
                self.app.notify("Formulación confirmada. Pasa a MIX y detén la mezcla en la banda.")
        elif event.type == pygame.MOUSEMOTION and self.active is not None:
            self.active.set_from_y(event.pos[1])
            self._push()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = None

    def _push(self) -> None:
        """Copia los tres sliders al GameState (y puede invalidar la mezcla)."""
        self.state.update_recipe(
            polymer=self.slider_by_key["polymer"].value,
            agent=self.slider_by_key["agent"].value,
            rpm=self.slider_by_key["rpm"].value,
        )

    def draw(self, surface) -> None:
        self.assets.blit_background(surface)
        draw_reminder(surface, self.assets.sm, self.state.order, self.state.service_time)
        for slider in self.sliders:
            slider.draw(surface, self.assets.sm, self.assets.md)
        recipe = self.state.recipe
        fill = self.physics.nivel_visual(recipe.polymer, recipe.agent)
        liquid = DYES.get(recipe.color, (214, 176, 214))
        eq = self.physics.estado_reologico(recipe.polymer, recipe.agent, recipe.rpm)
        Beaker.draw(
            surface,
            self.beaker,
            liquid,
            fill,
            self.app.time,
            viscosity=eq["mu"],
            rpm=recipe.rpm,
        )
        self._draw_colors(surface)
        self.confirm.label = "Formulación lista" if recipe.confirmed else "Confirmar Formulación"
        self.confirm.color = C["green"] if recipe.confirmed else C["purple"]
        self.confirm.draw(surface, self.assets.md, self.app.mouse)

    def _draw_colors(self, surface) -> None:
        blit(surface, self.assets.md, "Colorante", C["white"], (720, TOP_BAR_H + 64), "center", C["shadow"])
        selected = self.state.recipe.color
        for key, rect in self.color_rects.items():
            body = draw_candy_button(surface, rect, C["white"], self.app.mouse, active=key == selected)
            swatch = pygame.Rect(body.x + 10, body.centery - 11, 22, 22)
            pygame.draw.circle(surface, DYES[key], swatch.center, 11)
            pygame.draw.circle(surface, (40, 16, 56), swatch.center, 11, 2)
            blit(surface, self.assets.sm, COLOR_LABELS[key], (42, 28, 64), (body.x + 42, body.centery), "midleft")
