<!-- AI assisted development -->
# Slime Lab — qué es, cómo funciona y cómo seguirlo

Documento de contexto para continuar el proyecto en **otro Cursor / otro dispositivo**.  
Repositorio: [https://github.com/duvn0210/slime-lab](https://github.com/duvn0210/slime-lab)

---

## 1. Qué es

**Slime Lab** es un minijuego educativo en **Python 3.12 + Pygame 2.6**. El jugador es un técnico de laboratorio que recibe el pedido de un cliente y debe fabricar un slime (color, viscosidad y decoración).

No es un simulador científico exacto: usa un modelo **pedagógico** de fluido no newtoniano (dilución + ley de potencia) para que el alumno relacione:

- más polímero y más agente entrecruzante `[A]` → slime más espeso
- más RPM → más corte → **baja** la viscosidad aparente (pseudoplástico)
- hay que **detener la mezcla a tiempo** para clavar la banda de μ (Pa·s)

Idioma de la UI: **español**. Ventana fija **1024 × 600** a 60 FPS.

---

## 2. Cómo bajarlo y ejecutarlo (otro PC / Cursor)

```bash
git clone https://github.com/duvn0210/slime-lab.git
cd slime-lab
python3.12 -m venv .venv
# Windows: py -3.12 -m venv .venv && .\.venv\Scripts\Activate.ps1
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Dependencia real: solo `pygame>=2.5` (`requirements.txt`). El `.venv` no se versiona.

En Cursor: **File → Open Folder** sobre `slime-lab` (no hace falta un `.sln`). Punto de entrada: `main.py`.

---

## 3. Flujo del jugador

Hay **5 pantallas**. El cromo (barra superior e inferior) es común.

| Clave     | Estación | Qué hace el jugador |
|-----------|----------|---------------------|
| `order`   | ORDER    | Ve al cliente y el ticket del pedido (color, viscosidad baja/media/alta, adornos). Botón **Manual de Fórmulas**. |
| `build`   | BUILD    | Tres sliders: polímero (1–10 % p/v), agente (0.01–0.50 mol/L), RPM (10–200). Elige **colorante**. **Confirmar Formulación**. |
| `mix`     | MIX      | El agitador gira; μ sube hacia el equilibrio. Gráficas de μ(t) y τ(γ). **Detener Mezcla** fija `achieved_mu`. Espacio = detener. |
| `top`     | TOP      | Aplica decoraciones (clic o arrastrar al vaso). **Entregar Pedido**. |
| `result`  | RESULT   | Ticket de control de calidad y puntuación. **Nuevo Pedido**. |

Navegación: botones ORDER/BUILD/MIX/TOP, flechas de la barra superior, teclas `1–4`, ← →.  
Desde RESULT no se puede volver a las estaciones: hay que pulsar **Nuevo Pedido**.

**Pedido 1 (fijo, tutorial):** slime rosa, viscosidad **alta**, decoración **glitter**. El sprite del cliente sí puede variar.  
Pedidos siguientes: color, banda y 1–2 adornos aleatorios.

---

## 4. Arquitectura (cómo está hecho)

```
main.py              → bucle Pygame, cromo, pausa, manual, toasts
game_state.py        → Order, Recipe, monedas, mezcla, adornos
physics_engine.py    → dilución, ley de potencia, transitorio, scoring
settings.py          → constantes (no hardcodear magia en las pantallas)
assets_loader.py     → fondo, sprites de cliente, iconos vectoriales
ui_components.py     → botones candy, sliders, vaso/slime, gráficas
screens/*.py         → una clase por estación (hereda BaseScreen)
assets/              → PNG/JPG (fondo, clientes, mockups de referencia)
```

**Regla de capas**

- `SlimeLab` (`main.py`) posee `assets`, `physics`, `state` y el dict `screens`.
- Cada estación recibe `app` y usa `self.state` / `self.physics` / `self.assets`.
- **No** cambies las fórmulas de `physics_engine.py` salvo que el pedido pedagógico lo pida. La física es el “SET B” acordado (dilución + power law + transitorio).

Bucle (`SlimeLab.run`):

1. `clock.tick(60)` → `dt`
2. Eventos → cromo o `screens[current].handle_event`
3. Si no hay pausa/manual: `update(dt)` y `service_time += dt` (excepto en RESULT)
4. `draw`: fondo de estación + cromo + overlays

---

## 5. Física (qué calcula de verdad)

Todo vive en `SlimePhysics` (`physics_engine.py`). Constantes en `settings.py`.

### 5.1 Dilución

El slider de polímero es `V_base` (% p/v, 1–10). Hay un solvente fijo y el agente aporta volumen:

```
V_total = V_SOLVENT + V_base + [A] * V_AGENT_SCALE
C_final = (V_base * C_BASE) / V_total
```

Valores: `C_BASE=10`, `V_SOLVENT=15`, `V_AGENT_SCALE=10`.

Más agente **diluye** un poco (baja `C_final`) pero sube mucho `K` por el entrecruzamiento.

### 5.2 Ley de potencia (pseudoplástico)

```
K     = 1.2 * C_final^1.05 * (1 + 3.5 * [A])
n     = clamp(0.88 - 0.90*[A] - 0.006*C_final, 0.20, 0.90)
γ     = max(0.20, 0.15 * RPM)
τ     = K * γ^n
μ_ap  = K * γ^(n-1)     ← viscosidad aparente de equilibrio
```

Alta viscosidad de pedido: **más polímero, más [A], pocas RPM**.  
Baja: lo contrario.

### 5.3 Mezcla en el tiempo (estación MIX)

No aparece μ_eq de golpe:

```
τ_mix = 3.5 + 90 / RPM
μ(t)  = μ_eq * (1 - exp(-t / τ_mix))
```

Más RPM → llega antes al equilibrio (pero el equilibrio es **más bajo**).  
**Detener Mezcla** copia `current_mu` → `achieved_mu`. Eso es lo que se puntúa, no μ_eq.

### 5.4 Altura del líquido

Solo visual, no entra al score:

```
nivel = clamp(0.26 + 0.56*p + 0.10*a, 0.16, 0.92)
```

`p` y `a` son polímero y agente normalizados a sus sliders.

### 5.5 Bandas de calidad (Pa·s)

Definidas a mano para el juego, no medidas de laboratorio:

| Clave  | Rango     | Centro |
|--------|-----------|--------|
| baja   | 0.50–1.50 | 0.95   |
| media  | 1.85–3.40 | 2.50   |
| alta   | 4.80–8.80 | 6.30   |

En MIX la banda se pinta **verde** en la gráfica μ vs t. La línea punteada es μ_eq.

---

## 6. Puntuación

`calcular_puntuaciones` al entregar en TOP. Total 0–100.

| Rubro        | Máximo | Cómo |
|--------------|--------|------|
| Color        | 50     | 50 si el colorante coincide; 0 si no. |
| Viscosidad   | 50     | Dentro de banda: 36–50 según cercanía al centro. Fuera: hasta 30, cae con la distancia. |
| Decoración   | 10     | Proporción de adornos pedidos. **−2 por cada extra**. |
| Tiempo       | −16    | 120 s de gracia, luego −2 cada 8 s. **No se muestra** en la tarjeta QC (sí se aplica). |

Calificación: ≥90 `¡EXCELENTE!` (confeti), ≥70 `¡BUENO!`, si no `REGULAR`.  
Monedas: `round(total * 1.5)` y se acumulan en `GameState.coins`.

Cara del cliente en RESULT (overlay de boca sobre el PNG):

- `< 70` triste  
- `70–89` la sonrisa del sprite (mood `ok`)  
- `≥ 90` sonrisa más marcada  

En ORDER siempre mood `ok`.

---

## 7. UI y arte (decisiones que ya se tomaron)

**No** pegar capturas/mockups como fondo de pantalla completa (se pixelan y traen UI falsa).  
**Sí:**

- Fondo de laboratorio: `assets/fondo_slime.jpg` escalado a 1024×600 (`assets_loader._load_background`).
- UI nativa Pygame: tarjetas, botones **candy** 3D (`draw_candy_button`), sliders verticales (`CustomSlider`).
- Cliente: **sprites PNG recortados**, no siluetas dibujadas a código. Bustos (cabeza + torso), ángulo ¾/perfil.

### Clientes

| `sprite`   | Archivo                 | Nombre en chip |
|------------|-------------------------|----------------|
| `customer` | `assets/customer.png`   | cliente        |
| `mia`      | `assets/client_mia.png` | Mia            |
| `zack`     | `assets/client_zack.png`| Zack           |
| `layla`    | `assets/client_layla.png`| Layla         |
| `ben`      | `assets/client_ben.png` | Dr. Ben        |

Se eligen al azar **sin repetir el anterior**. Solo aparecen en ORDER y RESULT (no en BUILD/MIX/TOP).

### Vaso (`Beaker` en `ui_components.py`)

- Cilindro de vidrio cuya **boca elíptica coincide en ancho** con las paredes.
- Slime animado: oleaje, burbujas y remolino acoplados a **μ y RPM** (baja μ = más líquido; alta = jiggle lento).
- MIX: agitador (motor naranja, eje, paletas) si no hay tapa.
- TOP: sticker de seguridad, sello medalla, glitter/estrellas en el fluido, tapa rosa.

### Ticket de pedido vs QC

Misma familia visual: cabecera rosa, filas con icono, radio 22.  
RESULT: tres filas (color / viscosidad / decoración) y debajo, como el mockup:

- `75 / 100` grande  
- `¡BUENO!` (o la nota)  
- `+N monedas`  

**No** meter el tiempo en esa tarjeta.

Cromo: pausa y volumen **abajo a la derecha**. Arriba: flechas blanca/coral de estación, no pausa.

---

## 8. Mapa de archivos (dónde tocar qué)

| Archivo | Responsabilidad |
|---------|-----------------|
| `main.py` | App, nav, pausa, overlay del manual, teclas. |
| `settings.py` | Rangos, bandas, paleta, textos de estación. |
| `physics_engine.py` | Único sitio de fórmulas y scoring. |
| `game_state.py` | Pedido, receta, historial μ(t), adornos, entrega. |
| `ui_components.py` | Beaker, slime, batidor, stickers, charts, botones. |
| `assets_loader.py` | Carga de JPG/PNG, `draw_customer`, iconos 48px. |
| `screens/order_station.py` | Ticket + cliente + manual. |
| `screens/build_station.py` | Sliders y colorantes. |
| `screens/mix_station.py` | Charts, μ, vaso mezclando, detener. |
| `screens/top_station.py` | Herramientas, drag & drop, entregar. |
| `screens/result_station.py` | Ticket QC, confeti, nuevo pedido. |
| `screens/base_screen.py` | `BaseScreen`, `blit`, `fit_text`, reminder. |

`fix_assets.py` es un script viejo de Unsplash; **no** es el pipeline actual de arte.

Atribución: todo `.py` / `.md` / `.sh` creado o editado por IA lleva comentario de cabecera (`# AI assisted development` o `<!-- AI assisted development -->`). JSON no.

---

## 9. Estado del receta y trampas de implementación

Ciclo de vida típico:

1. Sliders → `update_recipe` (si cambian, **se invalida** `confirmed`, se resetea MIX y se limpian adornos).
2. Color → `set_color`.
3. Confirmar → `confirmed=True`, `reset_mix()`.
4. MIX `update`: si confirmed y no locked, avanza `mix_time` y `push_sample`.
5. Detener → `lock_mix()` guarda `achieved_mu`.
6. TOP: `applied` es un `set` de claves `glitter|stars|safety|seal|lid`.
7. Entregar exige: formulación confirmada, mezcla locked, color elegido.
8. `deliver(physics)` llena `last_report` y suma monedas.

Si el jugador vuelve a BUILD y mueve un slider, pierde la mezcla. Es intencional.

`current_mu` en MIX vale `0` hasta que empieza a girar (pedido no confirmado). El vaso usa entonces μ de equilibrio para el look.

---

## 10. Convenciones visuales / lo que ya se rechazó

No reabrir estos caminos sin que lo pidan:

- Fondos Unsplash o avatares geométricos.
- Mockup JPG como UI completa (cartas pixeladas).
- Dibujar el cliente con primitivas Pygame (el usuario pidió **superponer PNG**).
- Personajes de cuerpo entero: recortar a **busto**, como `customer.png`.
- Botones planos estilo IE; usar candy 3D.
- Pausa/volumen en la barra de título; van abajo.
- Física distinta (otro modelo de viscosidad) sin acuerdo.

Sí está bien: UI vectorial nativa + fondo ilustrado + sprites.

---

## 11. Atajos y overlays

- `Esc` pausa / cierra manual.
- Menú pausa: continuar, manual, salir.
- Manual: cuatro bloques (dilución, ley de potencia, bandas, cómo acertar). El reloj **se detiene** con el manual o la pausa.
- Toast (`app.notify`) ~2.8 s arriba.

Sonido: el botón existe (`sound_on`) pero **aún no hay audio** real.

---

## 12. Git

- Rama: `main`
- Remote: `origin` → `https://github.com/duvn0210/slime-lab.git`
- Commits: conventional (`feat`, `fix`, `docs`, `chore`).
- No commitear `.venv/`, `__pycache__/`, `*Zone.Identifier`.

En el otro dispositivo: `git clone` o `git pull` y abrir la carpeta en Cursor. Este archivo (`DOCUMENTACION.md`) es el briefing para el agente.

---

## 13. Ideas de continuación (no implementadas)

- Audio (clics, motor MIX, fanfarria EXCELENTE).
- Persistencia de récord/monedas.
- Más pedidos con historia o dificultad.
- Quitar mockups JPG de `assets/` si ya no se usan.
- Empaquetar (PyInstaller) para Windows.

La jugabilidad núcleo (ORDER→BUILD→MIX→TOP→RESULT + física SET B) **está completa**.
