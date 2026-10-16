# AI assisted development
"""Bucle principal y máquina de estados de Slime Lab."""

from __future__ import annotations

import pygame

from assets_loader import AssetLoader
from game_state import GameState
from physics_engine import SlimePhysics
from screens.base_screen import blit, draw_button, draw_star, panel, wrap_text
from ui_components import draw_candy_button
from screens.build_station import BuildStation
from screens.mix_station import MixStation
from screens.order_station import OrderStation
from screens.result_station import ResultStation
from screens.top_station import TopStation
from settings import (
    BOTTOM_BAR_H,
    C,
    FPS,
    HEIGHT,
    SCREEN_TITLES,
    STATION_META,
    STATION_ORDER,
    TIME_GRACE_S,
    TIME_PENALTY_MAX,
    TIME_PENALTY_STEP,
    TIME_STEP_S,
    TOP_BAR_H,
    VISCOSITY_BANDS,
    WIDTH,
)


class SlimeLab:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Slime Lab")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.assets = AssetLoader()
        self.physics = SlimePhysics()
        self.state = GameState()
        self.screens = {
            "order": OrderStation(self),
            "build": BuildStation(self),
            "mix": MixStation(self),
            "top": TopStation(self),
            "result": ResultStation(self),
        }
        self.current = "order"
        self.running = True
        self.paused = False
        self.manual = False
        self.time = 0.0
        self.mouse = (0, 0)
        self.toast = ""
        self.toast_ttl = 0.0
        self.sound_on = True
        bar_y = HEIGHT - BOTTOM_BAR_H + 8
        button_h = 50
        self.prev_rect = pygame.Rect(6, 4, 78, 48)
        self.next_rect = pygame.Rect(WIDTH - 84, 4, 78, 48)
        self.pause_rect = self.prev_rect
        self.menu_rect = pygame.Rect(10, bar_y, 78, button_h)
        self.nav = {}
        x = 98
        for key in STATION_ORDER:
            self.nav[key] = pygame.Rect(x, bar_y, 148, button_h)
            x += 156
        self.bottom_pause_rect = pygame.Rect(WIDTH - 118, bar_y + 4, 46, 42)
        self.sound_rect = pygame.Rect(WIDTH - 64, bar_y + 4, 46, 42)
        self.dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dim.fill((18, 8, 36, 150))
        self.manual_card = pygame.Rect(80, 36, WIDTH - 160, HEIGHT - 110)
        self.manual_close = pygame.Rect(self.manual_card.right - 44, self.manual_card.y + 10, 32, 32)
        self.pause_card = pygame.Rect(WIDTH // 2 - 190, 110, 380, 280)
        self.pause_actions = {
            "resume": pygame.Rect(self.pause_card.x + 40, self.pause_card.y + 70, 300, 44),
            "manual": pygame.Rect(self.pause_card.x + 40, self.pause_card.y + 126, 300, 44),
            "quit": pygame.Rect(self.pause_card.x + 40, self.pause_card.y + 182, 300, 44),
        }
        self._set_icon()

    def _set_icon(self) -> None:
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, C["pink"], (16, 18), 12)
        pygame.draw.rect(icon, (255, 255, 255), (13, 4, 6, 8), border_radius=2)
        pygame.display.set_icon(icon)

    def notify(self, text: str) -> None:
        self.toast = text
        self.toast_ttl = 2.8

    def go(self, name: str) -> None:
        if self.current == "result" and name != "result":
            self.notify("Cierra el reporte con Nuevo Pedido.")
            return
        if name not in self.screens:
            return
        self.current = name
        self.screens[name].on_enter()

    def next_order(self) -> None:
        self.state.new_order()
        self.current = "order"
        self.screens["build"].on_enter()
        self.screens["result"].on_enter()

    def run(self) -> None:
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self._dispatch(event)
            overlay = self.paused or self.manual
            if not overlay:
                self.time += dt
                self.screens[self.current].update(dt)
                if self.current != "result":
                    self.state.service_time += dt
            if self.toast_ttl > 0:
                self.toast_ttl = max(0.0, self.toast_ttl - dt)
            self._draw()
        pygame.quit()

    def _dispatch(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            self._on_key(event)
            return
        if self.paused:
            self._on_pause_click(event)
            return
        if self.manual:
            self._on_manual_click(event)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._chrome_click(event.pos):
                return
        self.screens[self.current].handle_event(event)

    def _on_key(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self.manual:
                self.manual = False
            elif self.paused:
                self.paused = False
            else:
                self.paused = True
            return
        if self.paused or self.manual:
            return
        shortcuts = {
            pygame.K_1: "order",
            pygame.K_2: "build",
            pygame.K_3: "mix",
            pygame.K_4: "top",
        }
        if event.key in shortcuts:
            self.go(shortcuts[event.key])
        elif event.key == pygame.K_LEFT:
            self._back()
        elif event.key == pygame.K_RIGHT:
            self._forward()
        elif event.key == pygame.K_SPACE and self.current == "mix":
            self.screens["mix"].toggle_lock()

    def _chrome_click(self, pos) -> bool:
        if self.menu_rect.collidepoint(pos) or self.bottom_pause_rect.collidepoint(pos):
            self.paused = True
            return True
        if self.sound_rect.collidepoint(pos):
            self.sound_on = not self.sound_on
            return True
        if self.prev_rect.collidepoint(pos):
            self._back()
            return True
        if self.next_rect.collidepoint(pos):
            self._forward()
            return True
        for key, rect in self.nav.items():
            if rect.collidepoint(pos):
                self.go(key)
                return True
        return False

    def _back(self) -> None:
        if self.current not in STATION_ORDER:
            return
        index = STATION_ORDER.index(self.current)
        if index > 0:
            self.go(STATION_ORDER[index - 1])

    def _forward(self) -> None:
        if self.current == "result":
            self.next_order()
            return
        if self.current not in STATION_ORDER:
            return
        index = STATION_ORDER.index(self.current)
        if index < len(STATION_ORDER) - 1:
            self.go(STATION_ORDER[index + 1])

    def _on_pause_click(self, event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.pause_actions["resume"].collidepoint(event.pos):
            self.paused = False
        elif self.pause_actions["manual"].collidepoint(event.pos):
            self.paused = False
            self.manual = True
        elif self.pause_actions["quit"].collidepoint(event.pos):
            self.running = False

    def _on_manual_click(self, event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.manual_close.collidepoint(event.pos) or not self.manual_card.collidepoint(event.pos):
            self.manual = False

    def _draw(self) -> None:
        self.assets.draw_station(self.screen, self.current)
        self.screens[self.current].draw(self.screen)
        self._draw_topbar()
        self._draw_bottombar()
        if self.toast_ttl > 0:
            self._draw_toast()
        if self.manual:
            self._draw_manual()
        if self.paused:
            self._draw_pause()
        pygame.display.flip()

    def _draw_topbar(self) -> None:
        bar = pygame.Surface((WIDTH, TOP_BAR_H), pygame.SRCALPHA)
        bar.fill((22, 12, 36, 235))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, C["pink"], (0, TOP_BAR_H - 1), (WIDTH, TOP_BAR_H - 1), 2)
        blit(self.screen, self.assets.lg, SCREEN_TITLES[self.current], C["white"], (WIDTH // 2, TOP_BAR_H // 2), "center")
        coin = pygame.transform.smoothscale(self.assets.icons["coin"], (22, 22))
        self.screen.blit(coin, (WIDTH - 200, 12))
        blit(self.screen, self.assets.md, str(self.state.coins), C["gold"], (WIDTH - 172, TOP_BAR_H // 2), "midleft")
        self._draw_nav_arrow(self.prev_rect, -1)
        self._draw_nav_arrow(self.next_rect, 1)

    def _draw_nav_arrow(self, rect, direction: int) -> None:
        """Flecha de estación al estilo del mockup: placa blanca y chevron coral."""
        hover = rect.collidepoint(self.mouse)
        body = rect.move(0, -1) if hover else rect
        radius = 14
        pygame.draw.rect(self.screen, (48, 22, 62), body.move(2, 3), border_radius=radius)
        pygame.draw.rect(self.screen, (252, 246, 250), body, border_radius=radius)
        pygame.draw.rect(self.screen, (72, 42, 88), body, 3, border_radius=radius)
        inner = body.inflate(-10, -10)
        pygame.draw.rect(self.screen, C["white"], inner, border_radius=9)
        pygame.draw.rect(self.screen, (228, 210, 220), inner, 2, border_radius=9)
        cx, cy = body.centerx, body.centery
        coral = (236, 78, 122)
        if direction < 0:
            points = [(cx + 10, cy - 13), (cx - 14, cy), (cx + 10, cy + 13)]
        else:
            points = [(cx - 10, cy - 13), (cx + 14, cy), (cx - 10, cy + 13)]
        pygame.draw.polygon(self.screen, coral, points)
        pygame.draw.lines(self.screen, (176, 40, 86), True, points, 3)

    def _round_button(self, rect, color) -> None:
        draw_candy_button(self.screen, rect, color, self.mouse, radius=min(14, rect.h // 2))

    def _draw_bottombar(self) -> None:
        bar = pygame.Surface((WIDTH, BOTTOM_BAR_H), pygame.SRCALPHA)
        bar.fill((18, 10, 30, 245))
        self.screen.blit(bar, (0, HEIGHT - BOTTOM_BAR_H))
        active_menu = self.paused
        self._station_button(self.menu_rect, "MENÚ", "", (124, 72, 196), active_menu, badge=None, star=False)
        for key, rect in self.nav.items():
            meta = STATION_META[key]
            enabled = self.current != "result"
            self._station_button(
                rect,
                meta["title"],
                meta["sub"],
                meta["color"] if enabled else (110, 110, 120),
                key == self.current,
                badge=None,
            )
        self._draw_order_badge()
        pause_body = draw_candy_button(self.screen, self.bottom_pause_rect, (255, 92, 168), self.mouse, radius=12)
        self._draw_pause_bars((pause_body.centerx, pause_body.y + int(pause_body.h * 0.38)))
        sound_body = draw_candy_button(self.screen, self.sound_rect, (110, 92, 210), self.mouse, radius=12)
        self._speaker((sound_body.centerx, sound_body.y + int(sound_body.h * 0.38)), self.sound_on)

    def _draw_order_badge(self) -> None:
        anchor = self.nav["order"]
        center = (anchor.x - 6, anchor.y + 10)
        number = str(self.state.order.number)
        draw_star(self.screen, center[0], center[1], 20, (96, 210, 64))
        draw_star(self.screen, center[0], center[1], 13, C["white"])
        font = self.assets.tiny if len(number) > 1 else self.assets.sm
        blit(self.screen, font, number, (36, 120, 48), center, "center")

    def _station_button(self, rect, title, subtitle, color, active, badge=None, star=False) -> None:
        drawn = draw_candy_button(
            self.screen,
            rect,
            color,
            self.mouse,
            label=title,
            font=self.assets.md,
            subtitle=subtitle,
            sub_font=self.assets.tiny,
            active=active,
        )
        if badge:
            center = (drawn.x + 16, drawn.y + 8)
            pygame.draw.circle(self.screen, C["white"], center, 11)
            pygame.draw.circle(self.screen, C["green"], center, 9)
            blit(self.screen, self.assets.tiny, badge, C["white"], center, "center")

    def _draw_pause_bars(self, center) -> None:
        x, y = center
        pygame.draw.rect(self.screen, C["white"], (x - 8, y - 8, 5, 16), border_radius=2)
        pygame.draw.rect(self.screen, C["white"], (x + 3, y - 8, 5, 16), border_radius=2)

    def _speaker(self, center, enabled) -> None:
        x, y = center
        pygame.draw.polygon(
            self.screen,
            C["white"],
            [(x - 7, y - 4), (x - 2, y - 4), (x + 5, y - 9), (x + 5, y + 9), (x - 2, y + 4), (x - 7, y + 4)],
        )
        if enabled:
            pygame.draw.arc(self.screen, C["white"], (x + 2, y - 7, 12, 14), -0.9, 0.9, 2)
        else:
            pygame.draw.line(self.screen, (255, 220, 230), (x + 3, y - 7), (x + 12, y + 7), 2)

    def _draw_toast(self) -> None:
        image = self.assets.sm.render(self.toast, True, C["ink"])
        rect = pygame.Rect(0, 0, image.get_width() + 36, 36)
        rect.center = (WIDTH // 2, 280)
        panel(self.screen, rect, C["gold"], C["ink"], radius=12, width=2)
        self.screen.blit(image, image.get_rect(center=rect.center))

    def _draw_pause(self) -> None:
        self.screen.blit(self.dim, (0, 0))
        panel(self.screen, self.pause_card, C["paper"], C["ink"], radius=18)
        blit(self.screen, self.assets.lg, "Pausa", C["ink"], (self.pause_card.centerx, self.pause_card.y + 36), "center")
        draw_button(self.screen, self.pause_actions["resume"], "Reanudar", self.assets.md, C["green"], self.mouse)
        draw_button(self.screen, self.pause_actions["manual"], "Manual de Fórmulas", self.assets.md, C["blue"], self.mouse)
        draw_button(self.screen, self.pause_actions["quit"], "Salir", self.assets.md, C["pink_deep"], self.mouse)

    def _draw_manual(self) -> None:
        self.screen.blit(self.dim, (0, 0))
        panel(self.screen, self.manual_card, C["paper"], C["ink"], radius=18)
        blit(self.screen, self.assets.lg, "Manual de Fórmulas", C["ink"], (self.manual_card.centerx, self.manual_card.y + 28), "center")
        pygame.draw.rect(self.screen, C["pink"], self.manual_close, border_radius=8)
        blit(self.screen, self.assets.md, "x", C["white"], self.manual_close.center, "center")
        y = self.manual_card.y + 58
        sections = self._manual_sections()
        for title, body, formula in sections:
            blit(self.screen, self.assets.md, title, C["pink_deep"], (self.manual_card.x + 28, y), "topleft")
            y += 26
            if formula:
                box = pygame.Rect(self.manual_card.x + 28, y, self.manual_card.w - 56, 28)
                pygame.draw.rect(self.screen, (244, 232, 250), box, border_radius=8)
                blit(self.screen, self.assets.mono, formula, C["ink"], box.center, "center")
                y += 36
            for line in wrap_text(self.assets.sm, body, self.manual_card.w - 64):
                blit(self.screen, self.assets.sm, line, C["ink"], (self.manual_card.x + 28, y), "topleft")
                y += 20
            y += 8

    def _manual_sections(self) -> list[tuple[str, str, str | None]]:
        bands = []
        for key in ("baja", "media", "alta"):
            band = VISCOSITY_BANDS[key]
            bands.append(f"{band['label']} {band['low']:.1f}–{band['high']:.1f} Pa·s")
        return [
            (
                "1. Balance de dilución",
                "V_base es el polímero base (1 a 10 % p/v). V_total crece cuando agregas agente entrecruzante [A] (0.01 a 0.50 mol/L), así que diluir demasiado baja C_final.",
                "C_final = (V_base · C_base) / V_total",
            ),
            (
                "2. Ley de potencia",
                "K, el índice de consistencia, sube con C_final y con [A]. n está entre 0.2 y 0.9: el slime es pseudoplástico. γ es proporcional a las RPM. A más velocidad de corte, la viscosidad aparente baja.",
                "τ = K·γ^n     μ_ap = K·γ^(n-1)",
            ),
            (
                "3. Bandas de calidad",
                "   ".join(bands) + f".  Tienes {int(TIME_GRACE_S)} s de gracia; después se restan {TIME_PENALTY_STEP} pts cada {int(TIME_STEP_S)} s (máximo -{TIME_PENALTY_MAX}). El reloj se detiene con el manual abierto.",
                None,
            ),
            (
                "4. Cómo acertar el pedido",
                "Viscosidad alta: más polímero, más [A] y pocas RPM. Viscosidad baja: lo contrario. En MIX, la curva sube hacia el equilibrio (línea punteada). Detén la mezcla cuando μ entre en la banda verde. Luego coloca solo los adornos que pidió el cliente.",
                None,
            ),
        ]


def main() -> None:
    SlimeLab().run()


if __name__ == "__main__":
    main()
