"""
game_state.py — la memoria del partido (el “modelo”).

Para qué sirve:
    Guarda lo que el jugador va haciendo: pedido del cliente, sliders, si ya
    confirmó, si ya detuvo MIX, adornos puestos, monedas y el último reporte.
    No dibuja y no tiene las fórmulas de μ (eso es physics_engine).

Conectado con:
    - main.py crea UN GameState y lo comparte con todas las pantallas
    - screens/* leen y escriben self.state
    - deliver() llama a physics.calcular_puntuaciones

Ciclo que deben poder explicar:
    sliders → update_recipe (si cambian, se pierde MIX)
    color → set_color
    Confirmar → confirmed=True, reset_mix
    MIX avanza mix_time / push_sample
    Detener → lock_mix (achieved_mu)
    TOP → applied (set de adornos)
    Entregar → deliver → last_report
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from settings import COLOR_LABELS, DECORATIONS, DYES, VISCOSITY_BANDS


CLIENT_SPRITES = ("customer", "mia", "zack", "layla", "ben")
CLIENT_NAMES = {
    "customer": "cliente",
    "mia": "Mia",
    "zack": "Zack",
    "layla": "Layla",
    "ben": "Dr. Ben",
}


@dataclass
class Order:
    """Pedido del cliente. viscosity es la clave 'baja'|'media'|'alta', no un número."""
    number: int
    color: str
    viscosity: str
    decorations: tuple[str, ...]
    name: str
    sprite: str

    @property
    def color_label(self) -> str:
        return COLOR_LABELS[self.color]

    @property
    def viscosity_label(self) -> str:
        return VISCOSITY_BANDS[self.viscosity]["label"]

    @property
    def decoration_label(self) -> str:
        return ", ".join(DECORATIONS[key] for key in self.decorations)


@dataclass
class Recipe:
    """Lo que el jugador eligió en BUILD. confirmed=False hasta pulsar Confirmar."""
    polymer: float = 5.0
    agent: float = 0.20
    rpm: float = 80.0
    color: str | None = None
    confirmed: bool = False


@dataclass
class GameState:
    coins: int = 0
    best: int = 0
    order_number: int = 0
    order: Order | None = None
    recipe: Recipe = field(default_factory=Recipe)
    mix_time: float = 0.0  # segundos mezclando (solo si confirmed y no locked)
    mix_locked: bool = False  # True = ya pulsó Detener; μ queda fija
    current_mu: float = 0.0  # μ ahora en MIX
    achieved_mu: float | None = None  # μ que entra al QC (al detener)
    history: list[tuple[float, float]] = field(default_factory=list)  # puntos (t, μ) de la gráfica
    applied: set[str] = field(default_factory=set)  # adornos en TOP
    service_time: float = 0.0  # reloj del pedido (main lo suma)
    last_report: dict | None = None  # lo que pinta RESULT
    _sample_acc: float = 0.0

    def __post_init__(self) -> None:
        if self.order is None:
            self.new_order()

    def new_order(self) -> Order:
        """Pedido 1 es tutorial (rosa, alta, glitter). Luego color/banda/adornos al azar."""
        self.order_number += 1
        sprite = self._pick_sprite()
        if self.order_number == 1:
            self.order = Order(
                number=1,
                color="rosa",
                viscosity="alta",
                decorations=("glitter",),
                name=CLIENT_NAMES[sprite] if sprite != "customer" else "cliente",
                sprite=sprite,
            )
        else:
            keys = list(DECORATIONS)
            n_extra = 1 if random.random() < 0.62 else 2
            self.order = Order(
                number=self.order_number,
                color=random.choice(list(DYES)),
                viscosity=random.choice(list(VISCOSITY_BANDS)),
                decorations=tuple(random.sample(keys, n_extra)),
                name=CLIENT_NAMES[sprite],
                sprite=sprite,
            )
        self.recipe = Recipe()
        self.reset_mix()
        self.applied.clear()
        self.service_time = 0.0
        self.last_report = None
        return self.order

    def _pick_sprite(self) -> str:
        pool = list(CLIENT_SPRITES)
        if self.order is not None and self.order.sprite in pool and len(pool) > 1:
            pool.remove(self.order.sprite)
        return random.choice(pool)

    def update_recipe(self, polymer: float, agent: float, rpm: float) -> None:
        """BUILD llama esto al mover sliders. Si cambian, se invalida MIX a propósito."""
        changed = (
            abs(self.recipe.polymer - polymer) > 1e-6
            or abs(self.recipe.agent - agent) > 1e-6
            or abs(self.recipe.rpm - rpm) > 1e-6
        )
        self.recipe.polymer = polymer
        self.recipe.agent = agent
        self.recipe.rpm = rpm
        if changed:
            self.recipe.confirmed = False
            self.reset_mix()
            self.applied.clear()

    def set_color(self, color: str) -> None:
        self.recipe.color = color

    def confirm(self) -> None:
        if self.recipe.confirmed:
            return
        self.recipe.confirmed = True
        self.reset_mix()

    def reset_mix(self) -> None:
        self.mix_time = 0.0
        self.mix_locked = False
        self.current_mu = 0.0
        self.achieved_mu = None
        self.history.clear()
        self._sample_acc = 0.0

    def push_sample(self, mu: float, dt: float) -> None:
        self.current_mu = mu
        self._sample_acc += dt
        if self._sample_acc >= 0.05 or not self.history:
            self._sample_acc = 0.0
            self.history.append((self.mix_time, mu))
            if len(self.history) > 1600:
                self.history = self.history[::2]

    def lock_mix(self) -> None:
        """Congela μ. El QC usa achieved_mu, no el equilibrio de la fórmula."""
        self.mix_locked = True
        self.achieved_mu = self.current_mu

    def toggle_decoration(self, key: str) -> None:
        if key in self.applied:
            self.applied.remove(key)
        else:
            self.applied.add(key)

    def deliver(self, physics) -> dict:
        """TOP llama esto al entregar. physics hace las cuentas; aquí solo se guardan."""
        report = physics.calcular_puntuaciones(
            color_pedido=self.order.color,
            color_obtenido=self.recipe.color,
            viscosidad_objetivo=self.order.viscosity,
            viscosidad_obtenida=self.achieved_mu,
            decoraciones_pedidas=self.order.decorations,
            decoraciones_aplicadas=self.applied,
            tiempo_servicio=self.service_time,
        )
        self.coins += report["monedas"]
        self.best = max(self.best, report["total"])
        self.last_report = report
        return report
