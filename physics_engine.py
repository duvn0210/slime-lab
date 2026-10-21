"""
Aquí está la “ciencia” del juego. Si el profesor pregunta dónde se calcula
si el slime queda líquido o espeso, la respuesta es este archivo.

No pinta botones ni sabe en qué pantalla estás. Solo recibe números
(polímero, agente, RPM, tiempo) y devuelve viscosidad y la nota.

Tres ideas, en palabras de cocina:

1) Dilución. Si echas más agua (el agente también ocupa espacio), la mezcla
   se aclara un poco. Fórmula: concentración final = (polímero × 10) / volumen total.

2) El slime no es miel normal. Cuanto más rápido lo agitas, más “flojo” se siente.
   Eso se llama pseudoplástico. Más RPM = viscosidad de equilibrio más baja.

3) El espesor no aparece de golpe. Sube hacia un tope (como calentar agua
   hacia una temperatura y quedarse ahí). La línea azul de MIX nunca pasa
   la punteada: se le pega.

La nota (color, viscosidad, adornos, penalización por tiempo) también se
saca aquí, al entregar el pedido.

Los números fijos (bandas 4.80–8.80, etc.) no están escritos a mano en cada
cuenta: se leen de settings.py.
"""

from __future__ import annotations

import math

from settings import (
    AGENT_MAX,
    AGENT_MIN,
    C_BASE,
    COIN_FACTOR,
    GAMMA_MIN,
    GAMMA_PER_RPM,
    GRADE_EXCELLENT,
    GRADE_GOOD,
    K_AGENT_GAIN,
    K_EXPONENT,
    K_PREFACTOR,
    MIX_TAU_BASE,
    MIX_TAU_RPM,
    N_AGENT_SLOPE,
    N_BASE,
    N_CONC_SLOPE,
    N_MAX,
    N_MIN,
    POLYMER_MAX,
    POLYMER_MIN,
    RPM_MAX,
    RPM_MIN,
    TIME_GRACE_S,
    TIME_PENALTY_MAX,
    TIME_PENALTY_STEP,
    TIME_STEP_S,
    V_AGENT_SCALE,
    V_SOLVENT,
    VISCOSITY_BANDS,
)


class SlimePhysics:
    """La calculadora. El juego no es un laboratorio real: es un modelo para enseñar la idea."""

    def volumen_total(self, v_base: float, agente: float) -> float:
        """Cuánto “ocupa” la mezcla: un líquido base + el polímero + un poco extra por el agente."""
        v_agent = max(0.0, agente) * V_AGENT_SCALE
        return V_SOLVENT + max(0.0, v_base) + v_agent

    def c_final(self, v_base: float, c_base: float, v_total: float) -> float:
        """Qué tan concentrado queda el polímero después de “diluir” con el resto del volumen."""
        if v_total <= 0.0:
            return 0.0
        return (v_base * c_base) / v_total

    def indice_consistencia(self, c_final: float, agente: float) -> float:
        """K: qué tan “cuerpo” tiene el slime en reposo. Sube con más polímero y más agente."""
        return K_PREFACTOR * (max(c_final, 0.0) ** K_EXPONENT) * (1.0 + K_AGENT_GAIN * max(agente, 0.0))

    def indice_flujo(self, c_final: float, agente: float) -> float:
        """
        n dice cómo reacciona al agitador. Si n es menor que 1 (aquí siempre),
        al agitar más rápido el slime se siente menos espeso. Más agente baja n.
        """
        n = N_BASE - N_AGENT_SLOPE * max(agente, 0.0) - N_CONC_SLOPE * max(c_final, 0.0)
        return max(N_MIN, min(N_MAX, n))

    def velocidad_corte(self, rpm: float) -> float:
        """Qué tan fuerte “corta” el agitador. Casi es: más RPM, más corte."""
        return max(GAMMA_MIN, GAMMA_PER_RPM * max(rpm, 0.0))

    def esfuerzo_corte(self, k: float, gamma: float, n: float) -> float:
        """La fuerza que hay que hacer para mover el slime a esa velocidad de agitador."""
        return k * (max(gamma, GAMMA_MIN) ** n)

    def viscosidad_aparente(self, k: float, gamma: float, n: float) -> float:
        """El número que ve el jugador: qué tan espeso se SIENTE el slime a esas RPM."""
        return k * (max(gamma, GAMMA_MIN) ** (n - 1.0))

    def estado_reologico(self, polymer: float, agente: float, rpm: float) -> dict:
        """Junta dilución + ley de potencia y te da la viscosidad de equilibrio de esa receta."""
        v_base = polymer
        v_total = self.volumen_total(v_base, agente)
        concentracion = self.c_final(v_base, C_BASE, v_total)
        k = self.indice_consistencia(concentracion, agente)
        n = self.indice_flujo(concentracion, agente)
        gamma = self.velocidad_corte(rpm)
        tau = self.esfuerzo_corte(k, gamma, n)
        mu = self.viscosidad_aparente(k, gamma, n)
        return {
            "v_base": v_base,
            "v_total": v_total,
            "c_final": concentracion,
            "K": k,
            "n": n,
            "gamma": gamma,
            "tau": tau,
            "mu": mu,
        }

    def viscosidad_en_tiempo(self, t: float, mu_eq: float, rpm: float) -> tuple[float, float]:
        """
        Cómo sube el espesor mientras mezclas. Empieza en 0 y se acerca al tope
        de esa receta (la línea de puntos). Nunca se pasa, como una olla que
        llega a hervir y se queda ahí. Si agitas más rápido, llega antes al
        tope, pero ese tope es más bajo (el slime se siente más líquido).
        """
        tau_mix = MIX_TAU_BASE + MIX_TAU_RPM / max(rpm, 1.0)
        progreso = 1.0 - math.exp(-max(0.0, t) / tau_mix)
        return mu_eq * progreso, tau_mix

    def curva_esfuerzo(self, polymer: float, agente: float, puntos: int = 40) -> list[tuple[float, float]]:
        """
        La gráfica de la derecha en MIX. No dice si ganaste o perdiste.
        Solo muestra: si agitaras más o menos rápido, cuánta “resistencia” tendría el slime.
        """
        estado = self.estado_reologico(polymer, agente, RPM_MIN)
        curva = []
        pasos = max(2, puntos)
        for i in range(pasos):
            rpm = RPM_MIN + (RPM_MAX - RPM_MIN) * i / (pasos - 1)
            gamma = self.velocidad_corte(rpm)
            tau = self.esfuerzo_corte(estado["K"], gamma, estado["n"])
            curva.append((gamma, tau))
        return curva

    def nivel_visual(self, polymer: float, agente: float) -> float:
        """Qué tan lleno se ve el vaso. Es solo dibujo: no entra en la nota."""
        span_p = max(0.001, POLYMER_MAX - POLYMER_MIN)
        span_a = max(0.001, AGENT_MAX - AGENT_MIN)
        p = (polymer - POLYMER_MIN) / span_p
        a = (agente - AGENT_MIN) / span_a
        return max(0.16, min(0.92, 0.26 + 0.56 * p + 0.10 * a))

    def calcular_puntuaciones(
        self,
        *,
        color_pedido: str,
        color_obtenido: str | None,
        viscosidad_objetivo: str,
        viscosidad_obtenida: float | None,
        decoraciones_pedidas: list[str] | tuple[str, ...],
        decoraciones_aplicadas: set[str],
        tiempo_servicio: float,
    ) -> dict:
        """
        Saca la nota del pedido.
        Color: 50 si acertaste el colorante, 0 si no.
        Viscosidad: hasta 50, según qué tan cerca quedaste de la banda pedida.
        Adornos: hasta 10; te restan 2 por cada sticker de más.
        Tiempo: después de 2 minutos empiezan a restar (eso no se escribe en la tarjeta).
        Si la suma pasa de 100, se deja en 100. Por eso 50+44+10 puede verse como 100.
        """
        color = 50 if color_obtenido and color_obtenido == color_pedido else 0
        banda = VISCOSITY_BANDS[viscosidad_objetivo]
        viscosidad = self._puntaje_viscosidad(viscosidad_obtenida, banda)
        decoracion = self._puntaje_decoracion(decoraciones_pedidas, decoraciones_aplicadas)
        penalizacion = self._penalizacion_tiempo(tiempo_servicio)
        subtotal = color + viscosidad + decoracion
        total = max(0, min(100, subtotal - penalizacion))
        return {
            "color": color,
            "viscosidad": viscosidad,
            "decoracion": decoracion,
            "penalizacion_tiempo": penalizacion,
            "subtotal": subtotal,
            "total": total,
            "calificacion": self.calificacion(total),
            "monedas": int(round(total * COIN_FACTOR)),
            "mu": viscosidad_obtenida,
            "banda": (banda["low"], banda["high"]),
            "banda_label": banda["label"],
        }

    def calificacion(self, total: int) -> str:
        """Pone el letrero: 90 o más EXCELENTE, 70 o más BUENO, si no REGULAR."""
        if total >= GRADE_EXCELLENT:
            return "¡EXCELENTE!"
        if total >= GRADE_GOOD:
            return "¡BUENO!"
        return "REGULAR"

    def _puntaje_viscosidad(self, mu: float | None, banda: dict) -> int:
        """Si caíste dentro del rango pedido, entre 36 y 50. Si te pasaste o te faltó, como mucho 30."""
        if mu is None:
            return 0
        low, high, center = banda["low"], banda["high"], banda["center"]
        if low <= mu <= high:
            half = max(center - low, high - center, 0.001)
            cercania = 1.0 - min(1.0, abs(mu - center) / half)
            return int(round(36 + 14 * cercania))
        ancho = max(0.001, high - low)
        distancia = (low - mu) if mu < low else (mu - high)
        return int(round(30 * max(0.0, 1.0 - distancia / ancho)))

    def _puntaje_decoracion(self, pedidas, aplicadas: set[str]) -> int:
        """Puntos por poner lo que pidió. Si pones extras (una tapa que no pidió), restan."""
        requeridas = set(pedidas)
        puestas = set(aplicadas)
        if not requeridas:
            return 10
        aciertos = len(requeridas & puestas)
        extras = len(puestas - requeridas)
        puntos = int(round(10 * aciertos / len(requeridas))) - 2 * extras
        return max(0, min(10, puntos))

    def _penalizacion_tiempo(self, tiempo: float) -> int:
        """Si tardas más de 2 minutos, restan puntos. Máximo 16. Eso no se ve en la tarjeta."""
        exceso = max(0.0, tiempo - TIME_GRACE_S)
        pasos = int(exceso / TIME_STEP_S)
        return min(TIME_PENALTY_MAX, pasos * TIME_PENALTY_STEP)
