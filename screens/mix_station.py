"""
Tercera pantalla: el entrecruzamiento mientras bates.

Química que se ve aquí (la calculadora sigue en physics_engine.py):
  - C_final: qué tan concentrado quedó el polímero después de diluir
  - [A]: el agente entrecruzante, en mol/L
  - n y K: la ley de potencia (si n < 1, a más corte el gel se siente más flojo)
  - γ: qué tan fuerte corta el agitador, en s⁻¹
  - ξ: qué fracción de la red ya se formó (0 % al empezar, 100 % en el equilibrio)

Gráfica izquierda: μ_ap contra el tiempo, en Pa·s y segundos.
  Verde = lo que pidió el cliente. Punteada = el equilibrio de TU receta.
  Las dos usan la misma escala vertical para poder compararlas con la derecha.

Gráfica derecha: curva de flujo, μ_ap contra γ.
  La misma franja verde. El punto rojo es tu agitador AHORA.
  Así comparas qué pasaría si giraras más rápido o más lento.

Espacio o el botón naranja = congelar μ_ap para la nota.
"""

from __future__ import annotations

import math

import pygame

from settings import BOTTOM_BAR_H, C, DYES, GAMMA_PER_RPM, HEIGHT, RPM_MAX, TOP_BAR_H, VISCOSITY_BANDS, WIDTH
from screens.base_screen import BaseScreen, blit, draw_reminder, panel, wrap_text
from ui_components import Beaker, Button, ProgressBar, axis_scale, draw_card, draw_chart


class MixStation(BaseScreen):
    def __init__(self, app) -> None:
        """Coloca las dos gráficas, la tarjeta de viscosidad, el vaso y el botón Detener."""
        super().__init__(app)
        self.angle = 0.0
        self.left_chart = pygame.Rect(8, TOP_BAR_H + 42, 300, 200)
        self.chem = pygame.Rect(8, TOP_BAR_H + 248, 300, 228)
        self._tips = []
        self.right_chart = pygame.Rect(548, TOP_BAR_H + 42, 468, 248)
        self.beaker = pygame.Rect(312, TOP_BAR_H + 56, 228, HEIGHT - BOTTOM_BAR_H - TOP_BAR_H - 120)
        self.progress = ProgressBar(pygame.Rect(548, TOP_BAR_H + 348, 468, 22))
        self.stop = Button(pygame.Rect(620, HEIGHT - BOTTOM_BAR_H - 48, 300, 40), "Detener Mezcla", C["orange"])

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
        flow = self.physics.curva_viscosidad(recipe.polymer, recipe.agent)
        # La misma escala en Pa·s en las dos gráficas: la franja verde queda a la misma altura.
        y_top = max(band["high"], eq["mu"], mu_now, max(point[1] for point in flow), 1.0)
        _y_axis, _y_ticks = axis_scale(y_top, 4)
        y_max = _y_axis
        x_time, _ = axis_scale(max(20.0, self.state.mix_time), 4)
        gamma_max = GAMMA_PER_RPM * RPM_MAX
        draw_chart(
            surface,
            self.left_chart,
            "Formación de la red",
            self.state.history,
            x_time,
            y_max,
            C["blue"],
            self.assets,
            band=(band["low"], band["high"]),
            dashed=eq["mu"],
            x_label="t (s)",
            y_label="μ_ap (Pa·s)",
        )
        draw_chart(
            surface,
            self.right_chart,
            "Curva de flujo  ·  punto = tu agitador",
            flow,
            gamma_max,
            y_max,
            C["pink"],
            self.assets,
            band=(band["low"], band["high"]),
            vline=eq["gamma"],
            marker=(eq["gamma"], mu_now if mu_now > 0 else 0.0),
            x_label="γ (s⁻¹)",
            y_label="μ_ap (Pa·s)",
        )
        self._draw_chem(surface, recipe, eq, band, mu_now)
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
        # ξ es la fracción de red formada. Lleno = equilibrio de la receta, no la nota.
        ratio = 0.0 if eq["mu"] <= 0 else max(0.0, min(1.0, mu_now / eq["mu"]))
        self.progress.draw(surface, ratio, self.assets.sm, "Entrecruzamiento ξ")
        if self.state.mix_locked:
            self.stop.label = "Reiniciar mezcla"
            self.stop.color = C["blue"]
        else:
            self.stop.label = "Detener Mezcla"
            self.stop.color = C["orange"]
        self.stop.draw(surface, self.assets.md, self.app.mouse)
        self._draw_tip(surface)

    def _info(self, surface, x, y, title: str, body: str, formula: str) -> None:
        """Circulito con una i. Si el mouse está encima, luego se dibuja el letrero."""
        rect = pygame.Rect(x, y, 14, 14)
        pygame.draw.circle(surface, (122, 86, 188), rect.center, 7)
        pygame.draw.circle(surface, C["white"], rect.center, 7, 1)
        mark = self.assets.tiny.render("i", True, C["white"])
        surface.blit(mark, mark.get_rect(center=rect.center))
        self._tips.append((rect.inflate(6, 6), title, body, formula))

    def _draw_tip(self, surface) -> None:
        """El letrero que sale al pasar el mouse por una i."""
        mouse = self.app.mouse
        for rect, title, body, formula in self._tips:
            if not rect.collidepoint(mouse):
                continue
            lines = wrap_text(self.assets.tiny, body, 250)
            width = 274
            height = 36 + len(lines) * 15 + 28
            box = pygame.Rect(rect.right + 8, rect.y - 8, width, height)
            if box.right > WIDTH - 8:
                box.right = rect.left - 8
            if box.bottom > HEIGHT - BOTTOM_BAR_H - 6:
                box.bottom = HEIGHT - BOTTOM_BAR_H - 6
            if box.top < TOP_BAR_H + 4:
                box.top = TOP_BAR_H + 4
            panel(surface, box, C["paper"], (122, 86, 188), radius=12, width=2)
            blit(surface, self.assets.sm, title, (122, 48, 150), (box.x + 12, box.y + 8), "topleft")
            y = box.y + 28
            for line in lines:
                blit(surface, self.assets.tiny, line, C["ink"], (box.x + 12, y), "topleft")
                y += 15
            formula_box = pygame.Rect(box.x + 10, y + 2, box.w - 20, 22)
            pygame.draw.rect(surface, (244, 232, 250), formula_box, border_radius=6)
            blit(surface, self.assets.tiny, formula, C["ink"], formula_box.center, "center")
            break

    def _draw_chem(self, surface, recipe, eq, band, mu_now) -> None:
        """La ficha química: concentración, agente, ley de potencia y cuánta red ya hay."""
        self._tips = []
        draw_card(surface, self.chem, C["white"], 15)
        xi = 0.0 if eq["mu"] <= 0 else max(0.0, min(1.0, mu_now / eq["mu"]))
        blit(surface, self.assets.sm, "Mezcla", C["muted"], (self.chem.x + 14, self.chem.y + 8), "topleft")
        blit(surface, self.assets.lg, f"{mu_now:.2f} Pa·s", C["ink"], (self.chem.x + 14, self.chem.y + 26), "topleft")
        self._info(
            surface,
            self.chem.x + 168,
            self.chem.y + 34,
            "Viscosidad aparente",
            "Qué tan espeso se siente el slime ahora, a las RPM de tu agitador. La nota usa este número cuando detienes la mezcla.",
            "μ_ap = K · γ^(n−1)",
        )
        inside = band["low"] <= mu_now <= band["high"] and mu_now > 0
        hint = "Dentro de la banda" if inside else f"Pedido {band['low']:.1f}–{band['high']:.1f} Pa·s"
        blit(
            surface,
            self.assets.sm,
            hint,
            C["good"] if inside else C["warn"],
            (self.chem.x + 14, self.chem.y + 58),
            "topleft",
        )
        rows = (
            (
                "Equilibrio",
                f"{eq['mu']:.2f} Pa·s",
                "Equilibrio",
                "El tope de tu receta: la línea punteada. La curva azul se le acerca y no la cruza.",
                "μ(t) → μ_eq",
            ),
            (
                "Concentración final",
                f"{eq['c_final']:.2f} % p/v",
                "Concentración final",
                "Cuánto polímero queda después de diluirlo con el solvente y el volumen del agente.",
                "C_final = (V_base · 10) / V_total",
            ),
            (
                "Agente entrecruzante",
                f"{recipe.agent:.2f} mol/L",
                "Agente entrecruzante",
                "Une las cadenas del polímero y forma la red. Si pones mucho, también diluye un poco.",
                "[A] en mol/L",
            ),
            (
                "Índice de flujo",
                f"{eq['n']:.2f}",
                "Índice de flujo",
                "Si n es menor que 1, el slime es pseudoplástico: a más corte se siente más flojo.",
                "n < 1",
            ),
            (
                "Índice de consistencia",
                f"{eq['K']:.2f}",
                "Índice de consistencia",
                "Qué tan cuerpo tiene el gel en la fórmula. Sube con la concentración y con el agente.",
                "K sube con C_final y [A]",
            ),
            (
                "Velocidad de corte",
                f"{eq['gamma']:.2f} s⁻¹",
                "Velocidad de corte",
                "Qué tan fuerte corta el agitador. Más RPM, más corte, y el slime se siente menos espeso.",
                "γ = 0.15 · RPM",
            ),
            (
                "Esfuerzo de corte",
                f"{eq['tau']:.2f} Pa",
                "Esfuerzo de corte",
                "La fuerza que hay que hacer para mover el slime a esa velocidad de corte.",
                "τ = K · γ^n",
            ),
            (
                "Entrecruzamiento",
                f"{xi * 100:.0f} %",
                "Grado de entrecruzamiento",
                "Qué fracción de la red ya se formó. 100 % es el equilibrio de tu receta, no la nota.",
                "ξ = 1 − exp(−t/τ)",
            ),
        )
        y = self.chem.y + 80
        for label, value, title, body, formula in rows:
            blit(surface, self.assets.tiny, label, C["ink"], (self.chem.x + 12, y), "topleft")
            blit(surface, self.assets.tiny, value, C["muted"], (self.chem.right - 30, y + 6), "midright")
            self._info(surface, self.chem.right - 24, y, title, body, formula)
            y += 18
