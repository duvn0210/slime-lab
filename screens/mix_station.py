"""
Tercera pantalla: mezclas y miras si el espesor entra en lo que pidió el cliente.

La gráfica de la IZQUIERDA es la importante:
  - Franja verde: el rango que pidió el cliente (por ejemplo 4.8 a 8.8)
  - Línea de puntos: el tope de TU receta (a dónde llegaría si nunca detienes)
  - Línea azul: cómo va subiendo el espesor ahora

La azul se curva y se pega a los puntos. Eso está bien: el slime llega a un
tope y se queda. Detén cuando la azul esté DENTRO del verde. No esperes a
que la barrita de abajo se llene: esa barrita es “qué tan cerca del tope”,
no “qué tan buena es la nota”.

La gráfica de la DERECHA no es un examen. Solo muestra cómo se comporta
el slime si agitaras más o menos rápido.

Espacio o el botón naranja = congelar el espesor para la nota.
"""

from __future__ import annotations

import math

import pygame

from settings import BOTTOM_BAR_H, C, DYES, HEIGHT, TOP_BAR_H, VISCOSITY_BANDS
from screens.base_screen import BaseScreen, blit, draw_reminder
from ui_components import Beaker, Button, ProgressBar, draw_card, draw_chart


class MixStation(BaseScreen):
    def __init__(self, app) -> None:
        """Coloca las dos gráficas, la tarjeta de viscosidad, el vaso y el botón Detener."""
        super().__init__(app)
        self.angle = 0.0
        self.left_chart = pygame.Rect(12, TOP_BAR_H + 48, 250, 168)
        self.right_chart = pygame.Rect(620, TOP_BAR_H + 48, 280, 168)
        self.mu_card = pygame.Rect(12, TOP_BAR_H + 224, 250, 96)
        self.beaker = pygame.Rect(290, TOP_BAR_H + 48, 220, HEIGHT - BOTTOM_BAR_H - TOP_BAR_H - 70)
        self.progress = ProgressBar(pygame.Rect(620, TOP_BAR_H + 236, 280, 22))
        self.stop = Button(pygame.Rect(650, HEIGHT - BOTTOM_BAR_H - 48, 220, 40), "Detener Mezcla", C["orange"])

    def handle_event(self, event) -> None:
        """Clic en Detener Mezcla (o Reiniciar si ya habías detenido)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.stop.hit(event.pos):
            self.toggle_lock()

    def toggle_lock(self) -> None:
        """Detener = “esta viscosidad cuenta”. Si ya habías detenido, Reiniciar te deja mezclar otra vez."""
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
        """Si confirmaste y no has detenido, avanza el tiempo y sube el espesor un poquito."""
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
        """Pinta las dos gráficas, el número de viscosidad, el vaso y el botón."""
        self.assets.blit_background(surface)
        draw_reminder(surface, self.assets.sm, self.state.order, self.state.service_time)
        recipe = self.state.recipe
        eq = self.physics.estado_reologico(recipe.polymer, recipe.agent, recipe.rpm)
        band = VISCOSITY_BANDS[self.state.order.viscosity]
        mu_now = self.state.current_mu
        y_max = max(band["high"] * 1.25, eq["mu"] * 1.15, mu_now * 1.1, 1.0)
        # Izquierda: espesor contra el tiempo. Verde = lo que pidió. Puntos = el tope de tu receta.
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
        # Derecha: no es la calificación. Es “si agito más rápido, ¿cuánta resistencia hay?”.
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
        # Esta barra llena = ya llegaste al tope de la receta, NO = nota perfecta.
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
        """La cajita: viscosidad de ahora, si estás en la banda, y el tope (eq)."""
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
