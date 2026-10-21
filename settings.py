"""
Esta es la lista de números del juego. No hay cuentas aquí: solo valores
que el resto del programa consulta, como un recetario.

Si el profesor pregunta “¿por qué viscosidad alta es de 4.80 a 8.80?”,
se lo mostramos en VISCOSITY_BANDS, más abajo. Esos rangos los inventamos
para que el juego se sienta bien; no salieron de un laboratorio real.

También están: tamaño de la ventana, hasta dónde llegan los sliders,
colores de los botones y cuántos puntos vale cada cosa.
"""

# Tamaño de la ventana en píxeles. FPS = cuántas veces por segundo se redibuja (como un flipbook).
WIDTH = 1024
HEIGHT = 600
FPS = 60

TOP_BAR_H = 46
BOTTOM_BAR_H = 68
REMINDER_Y = 54
REMINDER_H = 30

# Hasta dónde puedes mover cada slider en BUILD.
POLYMER_MIN = 1.0
POLYMER_MAX = 10.0
AGENT_MIN = 0.01
AGENT_MAX = 0.50
RPM_MIN = 10
RPM_MAX = 200

# Balance de dilución: C_final = (V_base * C_base) / V_total
# V_base es el % p/v del slider. V_total suma solvente y el volumen del agente.
C_BASE = 10.0
V_SOLVENT = 15.0
V_AGENT_SCALE = 10.0

# Números de la fórmula “cuanto más agitas, más líquido se siente” (pseudoplástico).
K_PREFACTOR = 1.2
K_EXPONENT = 1.05
K_AGENT_GAIN = 3.5
N_BASE = 0.88
N_AGENT_SLOPE = 0.90
N_CONC_SLOPE = 0.006
N_MIN = 0.20
N_MAX = 0.90
GAMMA_PER_RPM = 0.15
GAMMA_MIN = 0.20

# Qué tan rápido sube la curva azul. Con RPM bajas tarda un poco más, pero no tanto como para aburrir.
MIX_TAU_BASE = 2.0
MIX_TAU_RPM = 30.0

# Qué tan espeso pidió el cliente. Pa·s = unidad de viscosidad. El “centro” da más puntos.
VISCOSITY_BANDS = {
    "baja": {"label": "Baja", "low": 0.50, "high": 1.50, "center": 0.95},
    "media": {"label": "Media", "low": 1.85, "high": 3.40, "center": 2.50},
    "alta": {"label": "Alta", "low": 4.80, "high": 8.80, "center": 6.30},
}

# Reloj de servicio: 2 min de gracia, luego -2 pts cada 8 s (tope -16). No se ve en el ticket QC.
TIME_GRACE_S = 120.0
TIME_STEP_S = 8.0
TIME_PENALTY_STEP = 2
TIME_PENALTY_MAX = 16

GRADE_EXCELLENT = 90  # cara feliz + confeti
GRADE_GOOD = 70
COIN_FACTOR = 1.5  # monedas = round(total * 1.5)

# Paleta tomada de los mockups del laboratorio.
C = {
    "bg_top": (126, 64, 184),
    "bg_bottom": (214, 96, 176),
    "ink": (52, 28, 78),
    "muted": (110, 84, 132),
    "white": (255, 255, 255),
    "paper": (255, 250, 252),
    "pink": (236, 78, 154),
    "pink_deep": (196, 48, 122),
    "nav": (22, 12, 36),
    "green": (76, 175, 80),
    "purple": (156, 39, 176),
    "orange": (255, 152, 0),
    "blue": (3, 169, 244),
    "gold": (255, 214, 64),
    "shadow": (36, 12, 58),
    "glass": (226, 236, 248),
    "good": (46, 160, 96),
    "warn": (220, 120, 40),
    "bad": (200, 64, 86),
}

DYES = {
    "rosa": (236, 72, 146),
    "azul": (46, 132, 228),
    "morado": (154, 72, 214),
    "verde": (52, 186, 112),
    "naranja": (255, 138, 42),
    "amarillo": (246, 206, 52),
}

COLOR_LABELS = {
    "rosa": "Rosa",
    "azul": "Azul",
    "morado": "Morado",
    "verde": "Verde",
    "naranja": "Naranja",
    "amarillo": "Amarillo",
}

DECORATIONS = {
    "glitter": "Brillo",
    "stars": "Estrellas",
    "safety": "Etiqueta de seguridad",
    "seal": "Sello de calidad",
    "lid": "Tapa personalizada",
}

# Orden de las hojas al usar las flechas. La nota (result) no está: no se “hojea”, se llega al entregar.
STATION_ORDER = ("order", "build", "mix", "top")

STATION_META = {
    "order": {"title": "ORDER", "sub": "station", "color": C["green"]},
    "build": {"title": "BUILD", "sub": "station", "color": C["purple"]},
    "mix": {"title": "MIX", "sub": "station", "color": C["orange"]},
    "top": {"title": "TOP", "sub": "station", "color": C["blue"]},
}

SCREEN_TITLES = {
    "order": "Slime Lab",
    "build": "Estación de Formulación",
    "mix": "Estación de Formulación",
    "top": "Estación de Formulación",
    "result": "Slime Lab",
}

SCREEN_SUB = {
    "build": "Estación de Formulación",
    "mix": "Estación de Formulación",
    "top": "Estación de Formulación",
    "result": "Reporte de Control de Calidad",
}
