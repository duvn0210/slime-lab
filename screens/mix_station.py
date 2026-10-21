"""
screens/mix_station.py — estación MIX (la que más pregunta el profesor).

Para qué sirve:
    Mientras confirmed y no locked, cada frame avanza mix_time y calcula μ(t).
    Gráfica izquierda: viscosidad vs tiempo (verde = pedido, punteada = μ_eq).
    Gráfica derecha: esfuerzo de corte τ(γ) — no es la nota.
    Detener Mezcla (o Espacio, en main) guarda achieved_mu.

Conectado con:
    - physics.viscosidad_en_tiempo, estado_reologico, curva_esfuerzo
    - game_state.push_sample / lock_mix / reset_mix
    - ui_components.draw_chart, Beaker, ProgressBar
"""

from __future__ import annotations

import math

import pygame

from settings import BOTTOM_BAR_H, C, DYES, HEIGHT, TOP_BAR_H, VISCOSITY_BANDS
from screens.base_screen import BaseScreen, blit, draw_reminder
from ui_components import Beaker, Button, ProgressBar, draw_card, draw_chart


class MixStation(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.angle = 0.0
        self.left_chart = pygame.Rect(12, TOP_BAR_H + 48, 250, 168)
        self.right_chart = pygame.Rect(620, TOP_BAR_H + 48, 280, 168)
        self.mu_card = pygame.Rect(12, TOP_BAR_H + 224, 250, 96)
        self.beaker = pygame.Rect(290, TOP_BAR_H + 48, 220, HEIGHT - BOTTOM_BAR_H - TOP_BAR_H - 70)
        self.progress = ProgressBar(pygame.Rect(620, TOP_BAR_H + 236, 280, 22))
        self.stop = Button(pygame.Rect(650, HEIGHT - BOTTOM_BAR_H - 48, 220, 40), "Detener Mezcla", C["orange"])

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.stop.hit(event.pos):
            self.toggle_lock()

    def toggle_lock(self) -> None:
        """Detener fija μ. Si ya estaba fija, Reiniciar mezcla borra el historial."""
        recipe = self.state.recipe
        if not recipe.confirmed:
            self.app.notify("Confirma la formulación en BUILD antes de mezclar.")
            return
        if self.state.mix_locked:
            self.state.reset_mix()
            self.app.notify("Mezcla reiniciada.")
            return
        self.state.lock_mix()
        self.app.notify(f"Viscosidad fijada en {self.state.achieved_mu:.2f} Pa·s.")

    def update(self, dt: float) -> None:
        # main llama update 60 veces/s. Aquí es donde μ sube de verdad.
        recipe = self.state.recipe
        spinning = recipe.confirmed and not self.state.mix_locked
        if spinning:
            self.angle = (self.angle + recipe.rpm * dt * 0.45) % math.tau
            self.state.mix_time += dt
            eq = self.physics.estado_reologico(recipe.polymer, recipe.agent, recipe.rpm)
            mu, _tau = self.physics.viscosidad_en_tiempo(self.state.mix_time, eq["mu"], recipe.rpm)
            self.state.push_sample(mu, dt)
        elif not self.state.mix_locked:
            self.state.current_mu = 0.0

    def draw(self, surface) -> None:
        self.assets.blit_background(surface)
        draw_reminder(surface, self.assets.sm, self.state.order, self.state.service_time)
        recipe = self.state.recipe
        eq = self.physics.estado_reologico(recipe.polymer, recipe.agent, recipe.rpm)
        band = VISCOSITY_BANDS[self.state.order.viscosity]
        mu_now = self.state.current_mu
        y_max = max(band["high"] * 1.25, eq["mu"] * 1.15, mu_now * 1.1, 1.0)
        # Izquierda: μ(t). Verde = pedido. Punteada = tope de ESTA receta.
        draw_chart(
            surface,
            self.left_chart,
            "Viscosidad vs. tiempo",
            self.state.history,
            max(8.0, self.state.mix_time),
            y_max,
            C["blue"],
            self.assets,
            band=(band["low"], band["high"]),
            dashed=eq["mu"],
        )
        # Derecha: τ vs γ. No dice si ganaste; es la ley de potencia de la receta.
        curve = self.physics.curva_esfuerzo(recipe.polymer, recipe.agent)
        draw_chart(
            surface,
            self.right_chart,
            "Esfuerzo de corte",
            curve,
            max(point[0] for point in curve),
            max(point[1] for point in curve) * 1.1,
            C["pink"],
            self.assets,
        )
        self._draw_mu(surface, eq, band, mu_now)
        liquid = DYES.get(recipe.color, (214, 176, 214))
        fill = self.physics.nivel_visual(recipe.polymer, recipe.agent)
        mixing = recipe.confirmed and not self.state.mix_locked and self.state.mix_time > 0
        Beaker.draw(
            surface,
            self.beaker,
            liquid,
            fill,
            self.app.time,
            mixing=mixing,
            angle=self.angle,
            agitator=recipe.confirmed and "lid" not in self.state.applied,
            viscosity=mu_now if mu_now > 0 else eq["mu"],
            rpm=recipe.rpm,
        )
        # Barra = μ actual / μ equilibrio. Llena no significa “ganaste”.
        ratio = 0.0 if eq["mu"] <= 0 else max(0.0, min(1.0, mu_now / eq["mu"]))
        self.progress.draw(surface, ratio, self.assets.sm, "Avance al equilibrio")
        if self.state.mix_locked:
            self.stop.label = "Reiniciar mezcla"
            self.stop.color = C["blue"]
        else:
            self.stop.label = "Detener Mezcla"
            self.stop.color = C["orange"]
        self.stop.draw(surface, self.assets.md, self.app.mouse)

    def _draw_mu(self, surface, eq, band, mu_now) -> None:
        draw_card(surface, self.mu_card, C["white"], 15)
        blit(surface, self.assets.sm, "Viscosidad aparente", C["muted"], (self.mu_card.x + 16, self.mu_card.y + 12), "topleft")
        blit(
            surface,
            self.assets.tiny,
            f"eq {eq['mu']:.2f}",
            C["muted"],
            (self.mu_card.right - 12, self.mu_card.y + 14),
            "topright",
        )
        blit(surface, self.assets.lg, f"{mu_now:.2f} Pa·s", C["ink"], (self.mu_card.x + 16, self.mu_card.y + 38), "topleft")
        inside = band["low"] <= mu_now <= band["high"] and mu_now > 0
        hint = "Dentro de la banda" if inside else f"Objetivo {band['low']:.1f}–{band['high']:.1f}"
        blit(
            surface,
            self.assets.sm,
            hint,
            C["good"] if inside else C["warn"],
            (self.mu_card.x + 16, self.mu_card.bottom - 14),
            "bottomleft",
        )
