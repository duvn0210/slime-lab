"""
Este archivo es la libreta del laboratorio: recuerda TODO lo que va pasando
en un pedido, pero no dibuja nada y no hace las cuentas de viscosidad.

Qué guarda, en cristiano:
  - Qué pidió el cliente (color, si lo quiere espeso o líquido, adornos)
  - Qué pusiste en los sliders y qué colorante elegiste
  - Si ya diste “Confirmar formulación”
  - Cuánto tiempo llevas mezclando y en qué viscosidad te detuviste
  - Qué stickers le pusiste al vaso
  - Cuántas monedas tienes y qué nota sacaste

Las 5 pantallas leen y escriben AQUÍ. Por eso si cambias un slider en BUILD,
MIX se entera: no hay copias distintas, hay una sola libreta.

Ojo importante para el profesor: si vuelves a BUILD y mueves un slider,
el juego borra la mezcla a propósito. No puedes “arreglar” el slime a escondidas.
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
    """
    El ticket del cliente.
    viscosity no es un número: es la palabra 'baja', 'media' o 'alta'.
    El rango en Pa·s de esa palabra está en settings.py.
    """
    number: int
    color: str
    viscosity: str
    decorations: tuple[str, ...]
    name: str
    sprite: str

    @property
    def color_label(self) -> str:
        """Texto lindo para el ticket: 'Rosa' en vez de 'rosa'."""
        return COLOR_LABELS[self.color]

    @property
    def viscosity_label(self) -> str:
        """'Baja', 'Media' o 'Alta' para mostrar en pantalla."""
        return VISCOSITY_BANDS[self.viscosity]["label"]

    @property
    def decoration_label(self) -> str:
        """Lista de adornos en español, juntos con comas: 'Brillo, Tapa'."""
        return ", ".join(DECORATIONS[key] for key in self.decorations)


@dataclass
class Recipe:
    """
    Lo que tú formulaste: cuánto polímero, cuánto agente, qué tan rápido agitas
    y de qué color. confirmed empieza en no; pasa a sí cuando pulsas Confirmar.
    MIX no empieza a girar hasta que confirmed sea sí.
    """
    polymer: float = 5.0
    agent: float = 0.20
    rpm: float = 80.0
    color: str | None = None
    confirmed: bool = False


@dataclass
class GameState:
    """La libreta: un pedido, tu receta, la mezcla y la nota. Todas las pantallas leen de aquí."""
    coins: int = 0
    best: int = 0
    order_number: int = 0
    order: Order | None = None
    recipe: Recipe = field(default_factory=Recipe)
    mix_time: float = 0.0  # cuántos segundos lleva el agitador girando
    mix_locked: bool = False  # True = ya pulsé Detener; la viscosidad queda congelada
    current_mu: float = 0.0  # viscosidad de AHORA (la línea azul)
    achieved_mu: float | None = None  # viscosidad que se usa en la nota (al detener)
    history: list[tuple[float, float]] = field(default_factory=list)  # puntos para dibujar la gráfica
    applied: set[str] = field(default_factory=set)  # adornos puestos (brillo, tapa, etc.)
    service_time: float = 0.0  # reloj del pedido; si tardas mucho, restan puntos
    last_report: dict | None = None  # la nota que se ve en la última pantalla
    _sample_acc: float = 0.0

    def __post_init__(self) -> None:
        """Al crear la libreta, si no hay pedido todavía, arma el primero."""
        if self.order is None:
            self.new_order()

    def new_order(self) -> Order:
        """
        Empieza un pedido nuevo.
        El primero siempre es tutorial: slime rosa, viscosidad alta y brillo.
        Los siguientes salen al azar (color, espesor y 1 o 2 adornos).
        """
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
        """Elige un cliente al azar, sin repetir el de recién para que no se vea el mismo dos veces."""
        pool = list(CLIENT_SPRITES)
        if self.order is not None and self.order.sprite in pool and len(pool) > 1:
            pool.remove(self.order.sprite)
        return random.choice(pool)

    def update_recipe(self, polymer: float, agent: float, rpm: float) -> None:
        """
        Se llama cada vez que mueves un slider.
        Si cambiaste polímero, agente o RPM, el juego dice: “esa mezcla ya no vale”
        y te obliga a confirmar y mezclar otra vez. Es a propósito, no un bug.
        """
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
        """Guarda el colorante que tocaste (rosa, azul, etc.)."""
        self.recipe.color = color

    def confirm(self) -> None:
        """Botón Confirmar formulación: a partir de aquí MIX puede empezar a girar."""
        if self.recipe.confirmed:
            return
        self.recipe.confirmed = True
        self.reset_mix()

    def reset_mix(self) -> None:
        """Borra el tiempo de mezcla, la gráfica y la viscosidad congelada. Mezcla de cero."""
        self.mix_time = 0.0
        self.mix_locked = False
        self.current_mu = 0.0
        self.achieved_mu = None
        self.history.clear()
        self._sample_acc = 0.0

    def push_sample(self, mu: float, dt: float) -> None:
        """Guarda un puntito (tiempo, viscosidad) para dibujar la gráfica azul de MIX."""
        self.current_mu = mu
        self._sample_acc += dt
        if self._sample_acc >= 0.05 or not self.history:
            self._sample_acc = 0.0
            self.history.append((self.mix_time, mu))
            if len(self.history) > 1600:
                self.history = self.history[::2]

    def lock_mix(self) -> None:
        """
        Botón Detener Mezcla: copia la viscosidad de ahora y la deja fija.
        La nota usa ESA cifra, no “a dónde habría llegado si esperabas más”.
        """
        self.mix_locked = True
        self.achieved_mu = self.current_mu

    def toggle_decoration(self, key: str) -> None:
        """Si el adorno ya estaba, lo quita; si no, lo pone. Un clic en TOP."""
        if key in self.applied:
            self.applied.remove(key)
        else:
            self.applied.add(key)

    def deliver(self, physics) -> dict:
        """
        Entregar Pedido. Le pasa a la calculadora (physics) el color, la viscosidad
        detenida, los adornos y el tiempo. Guarda la nota y suma monedas.
        """
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
