# Guion del video — cómo funciona el código de Slime Lab

Grábalo compartiendo pantalla: Visual Studio a la izquierda (el código) y el juego a la derecha. Habla despacio. Este texto se puede leer casi tal cual.

Duración sugerida: 12–15 minutos.

---

## 0. Cómo grabar (tú, antes de empezar)

1. Abre `slime-lab` en Visual Studio.
2. Corre el juego: `.\.venv\Scripts\python.exe main.py`
3. Ten abiertos, en pestañas: `main.py`, `game_state.py`, `physics_engine.py`, `screens/order_station.py`.
4. Lee este guion. No improvises fórmulas.

---

## 1. Qué es el proyecto (1 min)

Decir:

> Slime Lab es un minijuego educativo en Python con Pygame. No es una página web. Es una ventana de 1024 por 600 que se redibuja 60 veces por segundo. El jugador es un técnico: recibe un pedido, formula el slime, mezcla, decora y entrega. El profesor nos pide relacionar polímero, agente entrecruzante y RPM con la viscosidad aparente de un fluido no newtoniano. El modelo es pedagógico, no un laboratorio real. Le llamamos SET B: dilución más ley de potencia más un transitorio de mezcla.

Mostrar: la ventana del juego en ORDER.

---

## 2. Mapa de archivos (2 min)

En el Explorador de Visual Studio, ir archivo por archivo:

| Archivo | Frase corta |
|---|---|
| `main.py` | El cerebro de la app: ventana, teclas, cambio de pantalla. |
| `settings.py` | Números fijos: tamaño, bandas de viscosidad, colores. |
| `game_state.py` | La memoria: el pedido de ahora, la receta, si ya mezclaste. |
| `physics_engine.py` | Las únicas fórmulas. Si el profesor pregunta “dónde está la física”, aquí. |
| `ui_components.py` | Cómo se ven botones, sliders, vaso y gráficas. |
| `assets_loader.py` | Carga el fondo y los PNG de los clientes. |
| `screens/` | Una clase por estación. |

Decir:

> La regla de capas es esta: las pantallas no calculan la viscosidad. Le piden el número a physics. Tampoco guardan el pedido: lo leen de state. main es el único que decide qué pantalla está activa.

---

## 3. Cómo se “conectan las interfaces” (3 min)

Abrir `main.py`, constructor de `SlimeLab`. Señalar:

```python
self.assets = AssetLoader()
self.physics = SlimePhysics()
self.state = GameState()
self.screens = {
    "order": OrderStation(self),
    ...
}
self.current = "order"
```

Decir:

> Al arrancar se crean tres objetos compartidos: arte, física y estado. Luego se crean las cinco estaciones y a cada una le pasamos self, o sea la app entera. Por eso cada pantalla puede hacer self.state o self.physics. No hay URLs ni servidores. Es el mismo programa en memoria.

Abrir `screens/base_screen.py`, clase `BaseScreen`. Señalar `state`, `assets`, `physics`.

Decir:

> Todas las estaciones heredan BaseScreen. Por eso todas tienen los mismos tres atajos. Cada una implementa handle_event (clics), update (si el tiempo avanza) y draw (pintar).

Abrir `main.py`, método `run`. Decir, señalando el while:

> Esto es el bucle de Pygame. Cada vuelta: espera al siguiente frame, lee el mouse, reparte eventos, si no estamos en pausa actualiza la estación actual, y al final dibuja. Dibujar es: fondo, luego screens[current].draw, luego las barras de arriba y abajo.

Abrir `go`. Decir:

> Cambiar de interfaz es cambiar un string: current = "build". No se destruye la pantalla. La próxima vez que dibuje, usa otra clase. Desde RESULT no te deja volver: te manda el toast de Nuevo Pedido. Eso es intencional para no retocar el slime después de ver la nota.

Mostrar en el juego: clicar ORDER, BUILD, MIX, TOP. Decir que esos botones están en main, no en cada estación (`_chrome_click`).

---

## 4. Recorrido ORDER → RESULT (5 min)

### ORDER

Abrir `screens/order_station.py`. Mostrar el ticket.

> ORDER solo lee state.order. El primer pedido está fijo en game_state.new_order: rosa, viscosidad alta, glitter. Los siguientes salen al azar. El cliente es un PNG. El botón Manual no es una estación: pone app.manual = True y main dibuja el overlay. El reloj se detiene con el manual.

### BUILD

Abrir `build_station.py` y `game_state.update_recipe`.

> Tres sliders escriben polímero, agente y RPM. Colorante llama set_color. Confirmar pone confirmed True y reinicia la mezcla. Si vuelves y mueves un slider, confirmed pasa a False y se pierde MIX. El vaso es solo visual: la altura usa physics.nivel_visual, que no entra al puntaje.

### MIX

Abrir `mix_station.py` update y `physics.viscosidad_en_tiempo`.

> MIX es la única que usa update de verdad. Si confirmaste y no has detenido, avanza mix_time y calcula μ. La gráfica izquierda es μ contra tiempo. Verde = banda del cliente. Punteada = equilibrio de esta receta. La azul se acerca a la punteada con una exponencial y no la cruza. Eso está bien: el slime llega a un tope y se queda. La gráfica derecha es esfuerzo de corte, una propiedad de la receta, no la nota. Detener Mezcla guarda achieved_mu. El QC usa eso, no el equilibrio. Espacio hace lo mismo.

### TOP

Abrir `top_station.py` `_deliver`.

> Los adornos son un set. Clic alterna; arrastrar al vaso también. Entregar revisa tres cosas: formulación confirmada, mezcla detenida, color elegido. Si falta alguna, hay un toast. Si está bien, deliver pide a physics el reporte, suma monedas y salta a RESULT.

### RESULT

Abrir `result_station.py`.

> Pinta last_report. Cara del cliente: triste si menos de 70, normal si 70 a 89, más sonrisa si 90 o más. Nuevo Pedido llama next_order: pedido nuevo, receta en blanco, otra vez ORDER.

---

## 5. Física en palabras fáciles (2 min)

Abrir `physics_engine.py` y `settings.py`.

> Tres ideas. Primera, dilución: C_final = (V_base por C_base) sobre V_total. El agente ocupa volumen, así que diluye un poco, pero entrecruza y sube K. Segunda, ley de potencia: tau = K por gamma a la n. Mu aparente es K por gamma a la n menos 1. Como n es menor que 1, si agitas más rápido el slime se siente menos espeso. Eso es pseudoplástico. Tercera, el tiempo: mu no aparece de golpe. Sube hacia el equilibrio. A más RPM llega antes, pero el equilibrio es más bajo.

Receta para el profesor:

> Viscosidad alta: más polímero, más agente, pocas RPM, y detener cuando la azul entre en el verde. Viscosidad baja: lo contrario.

---

## 6. Cómo se saca la nota (1 min)

Abrir `calcular_puntuaciones`.

> Color 50 o 0. Viscosidad hasta 50: si estás en la banda, entre 36 y 50 según qué tan cerca del centro. Si estás fuera, hasta 30 y cae. Decoración 10, menos 2 por cada adorno de más. Tiempo: 120 segundos de gracia, luego menos 2 cada 8 segundos, máximo menos 16. Eso no se imprime en el ticket, pero sí se resta. El total se recorta entre 0 y 100. Por eso puedes ver 50 + 44 + 10 y aun así 100: 104 se corta.

---

## 7. Preguntas que puede hacer el profesor

**¿Es MVC?**  
Parecido. Vista = screens + ui. Modelo = game_state + physics. Controlador = main y los handle_event. No usamos un framework MVC.

**¿Dónde está el “frontend” y el “backend”?**  
No hay. Todo es un cliente Pygame. La “lógica de negocio” es physics_engine y game_state.

**¿Por qué no Unity?**  
El curso pide ver las fórmulas. En Python se leen en un archivo. Pygame pinta la ventana.

**¿El slime es física real de partículas?**  
No. El vaso anima oleaje según μ y RPM. La altura no puntúa. La ciencia está en las fórmulas de μ.

**¿Por qué la curva no cruza la punteada?**  
Porque μ(t) = μ_eq veces (1 menos e a la menos t sobre tau). Nunca pasa el equilibrio. La banda verde es otra cosa: es el pedido.

**¿Se puede hacer trampa volviendo a BUILD?**  
Si mueves sliders se borra la mezcla. RESULT no deja volver. Hay que hacer Nuevo Pedido.

**¿Hay sonido?**  
El botón existe (sound_on) pero no hay audio todavía.

**¿Dónde están los números de las bandas?**  
`settings.py`, VISCOSITY_BANDS. Baja 0.50–1.50, media 1.85–3.40, alta 4.80–8.80. Son bandas de juego, no mediciones de lab.

**Punto de entrada**  
`main.py`, `if __name__ == "__main__"`. Dependencia: pygame en `requirements.txt`. Python 3.12.

---

## 8. Cierre (20 s)

> En una frase: main elige la pantalla, las pantallas dibujan y toman clics, game_state recuerda el pedido y la receta, physics_engine calcula viscosidad y nota. Si el profesor pregunta “dónde está X”, vamos al archivo de esa capa y no mezclamos.
