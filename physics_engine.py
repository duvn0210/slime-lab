"""Reología del slime: dilución estequiométrica, ley de potencia y puntuación."""

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
    """Modelo pedagógico del fluido no newtoniano que sintetiza el laboratorio."""

    def volumen_total(self, v_base: float, agente: float) -> float:
        """Solvente de referencia + polímero dosificado + aporte del entrecruzante."""
        v_agent = max(0.0, agente) * V_AGENT_SCALE
        return V_SOLVENT + max(0.0, v_base) + v_agent

    def c_final(self, v_base: float, c_base: float, v_total: float) -> float:
        """Balance de dilución: C_final = (V_base * C_base) / V_total."""
        if v_total <= 0.0:
            return 0.0
        return (v_base * c_base) / v_total

    def indice_consistencia(self, c_final: float, agente: float) -> float:
        """K proporcional a la concentración final y al agente entrecruzante [A]."""
        return K_PREFACTOR * (max(c_final, 0.0) ** K_EXPONENT) * (1.0 + K_AGENT_GAIN * max(agente, 0.0))

    def indice_flujo(self, c_final: float, agente: float) -> float:
        """n en (0.2, 0.9): pseudoplástico. Más [A] y más polímero reducen n."""
        n = N_BASE - N_AGENT_SLOPE * max(agente, 0.0) - N_CONC_SLOPE * max(c_final, 0.0)
        return max(N_MIN, min(N_MAX, n))

    def velocidad_corte(self, rpm: float) -> float:
        """γ proporcional a las RPM del agitador."""
        return max(GAMMA_MIN, GAMMA_PER_RPM * max(rpm, 0.0))

    def esfuerzo_corte(self, k: float, gamma: float, n: float) -> float:
        """Ley de potencia: τ = K · γ^n."""
        return k * (max(gamma, GAMMA_MIN) ** n)

    def viscosidad_aparente(self, k: float, gamma: float, n: float) -> float:
        """μ_ap = K · γ^(n - 1)."""
        return k * (max(gamma, GAMMA_MIN) ** (n - 1.0))

    def estado_reologico(self, polymer: float, agente: float, rpm: float) -> dict:
        """Evalúa dilución y ley de potencia para una formulación."""
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
        """Acercamiento exponencial al equilibrio. A más RPM, menor constante de tiempo."""
        tau_mix = MIX_TAU_BASE + MIX_TAU_RPM / max(rpm, 1.0)
        progreso = 1.0 - math.exp(-max(0.0, t) / tau_mix)
        return mu_eq * progreso, tau_mix

    def curva_esfuerzo(self, polymer: float, agente: float, puntos: int = 40) -> list[tuple[float, float]]:
        """Curva de flujo de equilibrio τ(γ) sobre el rango operativo de RPM."""
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
        """Altura del líquido en la probeta, solo para la representación."""
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
        """Reporte de control de calidad. El total se recorta al rango 0–100."""
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
        if total >= GRADE_EXCELLENT:
            return "¡EXCELENTE!"
        if total >= GRADE_GOOD:
            return "¡BUENO!"
        return "REGULAR"

    def _puntaje_viscosidad(self, mu: float | None, banda: dict) -> int:
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
        requeridas = set(pedidas)
        puestas = set(aplicadas)
        if not requeridas:
            return 10
        aciertos = len(requeridas & puestas)
        extras = len(puestas - requeridas)
        puntos = int(round(10 * aciertos / len(requeridas))) - 2 * extras
        return max(0, min(10, puntos))

    def _penalizacion_tiempo(self, tiempo: float) -> int:
        exceso = max(0.0, tiempo - TIME_GRACE_S)
        pasos = int(exceso / TIME_STEP_S)
        return min(TIME_PENALTY_MAX, pasos * TIME_PENALTY_STEP)
