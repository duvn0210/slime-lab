# Guion del video — Slime Lab, explicado como a niños de 10 años

Este texto se puede leer casi tal cual. Habla despacio. Si te trabas, para el video y sigue desde el siguiente párrafo.

Imagina que le estás contando el juego a un primo pequeño: **no uses palabras raras sin explicarlas**. Cuando tengas que decir un nombre de archivo, dilo y luego tradúcelo (“esto es la libreta”).

Duración sugerida: **18 a 22 minutos**. Si se alarga, está bien: es mejor que se entienda.

---

## Cómo grabar (tú, antes de darle play)

1. Abre la carpeta `slime-lab` en Visual Studio.
2. Corre el juego: `.\.venv\Scripts\python.exe main.py`
3. Pon el juego a la **derecha** de la pantalla y el código a la **izquierda**.
4. Ten abiertas estas pestañas: `main.py`, `game_state.py`, `physics_engine.py`, `settings.py`, `screens/order_station.py`, `screens/build_station.py`, `screens/mix_station.py`.
5. Empieza un pedido nuevo (rosa, viscosidad alta, brillo) para que el ejemplo sea el mismo siempre.

Si el profesor o los compañeros miran, **señala con el mouse** lo que estás nombrando. No leas fórmulas en silencio.

---

## 1. Arranque: qué es este programa (1 min 30 s)

**Mostrar:** la ventana del juego en ORDER (el cliente y el ticket).

Decir:

> Hola. Esto es Slime Lab. Es un minijuego que hicimos en Python. Python es el idioma en el que le escribimos instrucciones a la computadora, como si le diéramos recetas a un robot.
>
> Pygame es una caja de herramientas para hacer ventanas, dibujos y clics. No es una página de internet. No hay Wi‑Fi ni servidor. Todo vive en esta ventanita de mil veinticuatro por seiscientos píxeles. Un píxel es un puntito de color en la pantalla.
>
> El juego se redibuja unas sesenta veces por segundo. Es como un flipbook: muchas fotitos seguidas y parece que el slime se mueve.
>
> Tú eres un técnico de laboratorio. Un cliente te pide un slime de un color, más líquido o más espeso, y con unos stickers. Tú lo armas, lo mezclas, lo decoras y se lo entregas. La computadora te pone una nota.

---

## 2. La idea más importante: el juego es un cuaderno con cinco hojas (2 min)

**Mostrar:** los botones de abajo: ORDER, BUILD, MIX, TOP.

Decir:

> Miren abajo. Esos cuatro botones no son cuatro programas distintos. Es **un solo programa** con cinco hojas, como un cuaderno.
>
> Primera hoja, ORDER: el cliente te pasa el pedido. Segunda, BUILD: tú echas los ingredientes. Tercera, MIX: bates y miras si quedó del espesor correcto. Cuarta, TOP: le pegas stickers y entregas. Quinta, RESULT: te ponen la nota, como el control de calidad.
>
> Cuando haces clic en BUILD, no se abre otra aplicación. Solo damos vuelta la hoja. El pedido sigue siendo el mismo, porque está escrito en una sola libreta que todas las hojas pueden leer.

Señalar en el Explorador de Visual Studio la carpeta `screens`.

> Cada hoja tiene su propio archivo dentro de la carpeta screens. screens significa “pantallas”. order_station es la hoja del cliente. build_station es la de los sliders. mix_station la de las gráficas. top_station la de los stickers. result_station la de la nota.
>
> Hay un archivo extra que se llama base_screen. Ese es el molde. Es como el patrón de una galleta: las cinco hojas salen del mismo cortador, para no copiar las mismas instrucciones cinco veces.

---

## 3. Los cuatro oficios del código (3 min)

**Mostrar:** el Explorador, ir archivo por archivo, lento.

Decir:

> El código no es un montón de letras sueltas. Es un equipo de cuatro oficios. Si se acuerdan de estos cuatro, ya entendieron cómo se conecta todo.

### Oficio 1 — El director (`main.py`)

> main.py es el director de la obra. Abre la ventana, pone el título “Slime Lab”, mira el mouse, oye las teclas y decide qué hoja se ve. También pinta las barritas de arriba y de abajo: las monedas, las flechas, MENÚ, pausa. Esas barritas no son de ninguna estación: son del director, para que se vean iguales en todas las hojas.

### Oficio 2 — La libreta (`game_state.py`)

> game_state es la libreta del laboratorio. Recuerda: qué pidió el cliente, qué pusiste en los sliders, si ya confirmaste, cuánto tiempo llevas batiendo, en qué espesor te detuviste, qué stickers pegaste, cuántas monedas tienes y qué nota sacaste.
>
> Ninguna hoja guarda eso por su cuenta. Todas preguntan a la misma libreta. Por eso, si en BUILD eliges color rosa, en MIX el vaso sigue rosa. No se lo tienen que contar por teléfono: leen el mismo cuaderno.

### Oficio 3 — La calculadora (`physics_engine.py`)

> physics_engine es la calculadora. No pinta botones. No sabe si estás en MIX o en TOP. Solo recibe números —cuánto polímero, cuánto agente, qué tan rápido giras— y responde: “este slime se siente de tanto espesor” y, al final, “tu nota es esta”.
>
> Si el profesor pregunta “¿dónde está la ciencia?”, señalamos este archivo. Las pantallas no inventan la viscosidad. Se la piden a la calculadora.

### Oficio 4 — Los crayones (`ui_components.py` + `assets_loader.py`)

> ui_components son los crayones: cómo se ve un botón gordito, un slider, el vaso de vidrio y las gráficas.
>
> assets_loader es la caja de fotos: el laboratorio de fondo, las caras de Mia, Zack, Layla y el doctor Ben, las letritas y los iconitos de moneda y matraz.
>
> Y hay un archivo que no hace nada de “trabajo”, solo es la lista de números: settings.py. Ahí está el tamaño de la ventana, hasta dónde llegan los sliders y los rangos de viscosidad. Es el recetario. Si el profesor pregunta “¿por qué alta es de 4.80 a 8.80?”, abrimos settings.py, no las pantallas.

**Mostrar** `settings.py` un segundo, `VISCOSITY_BANDS`.

---

## 4. Cómo se conectan las interfaces (el truco del video) (4 min)

Esta parte es la más importante. No la corras.

**Mostrar:** `main.py`, el constructor, estas líneas:

```python
self.assets = AssetLoader()
self.physics = SlimePhysics()
self.state = GameState()
self.screens = {
    "order": OrderStation(self),
    "build": BuildStation(self),
    ...
}
self.current = "order"
```

Decir, señalando cada línea:

> Al encender el juego pasa esto, una sola vez, en orden.
>
> Primero: carga las fotos. Segundo: arma la calculadora. Tercero: abre la libreta en blanco y escribe el primer pedido. Cuarto: crea las cinco hojas y a cada hoja le pasa self. self significa “yo, el juego entero”. Es como darle a cada hoja una llave de la misma casa.
>
> Por eso después, dentro de una hoja, pueden decir self.state y están leyendo la libreta, o self.physics y están usando la calculadora, o self.assets y pegan una foto. No hay internet. Es memoria de la misma computadora, el mismo programa.
>
> current es un letrerito que dice qué hoja está abierta. Empieza en order. Cambiar de interfaz es cambiar esa palabrita. No se tira la hoja anterior a la basura. Sigue viva, solo que no se pinta.

**Mostrar:** `screens/base_screen.py`, la clase `BaseScreen`, las propiedades `state`, `assets`, `physics`.

> Aquí está el atajo. Las cinco hojas heredan este molde. Heredar quiere decir: “yo también soy una BaseScreen, así que ya sé preguntarle al juego por la libreta, las fotos y la calculadora”. No copiamos ese código cinco veces.

**Mostrar:** `main.py`, el método `run`, el `while`.

> Esto es el corazón. Un while es un “repite esto hasta que cierre la ventana”. Cada vueltita, unas sesenta por segundo, el director hace cuatro preguntas:
>
> Uno: ¿pasó un segundo? Guarda un pedacito de tiempo que llamamos dt, “cuánto duró esta fotito”.
>
> Dos: ¿el jugador hizo clic o apretó una tecla? Si el clic fue en ORDER o en pausa, lo atiende el director. Si fue dentro de la hoja, se lo pasa a la hoja: handle_event. handle_event significa “atiende lo que acaba de pasar”.
>
> Tres: si no estamos en pausa ni en el manual, le dice a la hoja actual: update. update significa “avanza un poquito”. MIX es la única que de verdad usa esto: sube el espesor. Las otras casi no hacen nada aquí.
>
> Cuatro: pinta. Fondo, luego la hoja actual con draw, luego las barras, luego el avisito amarillo si hay uno. draw significa “dibújate”.
>
> Eso es todo el juego, para siempre, hasta que cierras.

**Mostrar:** el método `go`.

> go es “cambia de hoja”. Le pones el nombre: build, mix, top. Si ya estás viendo la nota, no te deja volver. Te sale un avisito: cierra el reporte con Nuevo Pedido. Eso es a propósito, para que no hagas trampa retocando el slime después de ver el puntaje.

**Mostrar en el juego:** clic en ORDER, BUILD, MIX, TOP. Volver a señalar `main.py`, `_chrome_click`.

> Estos botones de abajo no están dentro de cada estación. Están en el director. chrome, en este código, significa el marco: las barras. Así las cuatro hojas no pelean por pintar el menú.

---

## 5. Recorrido jugando: de ORDER a RESULT (7 min)

Ahora juega despacio y ve al código de esa hoja.

### ORDER — el ticket

**Mostrar:** el juego en ORDER. Luego `screens/order_station.py`.

> Esta hoja casi no piensa. Solo lee la libreta: “¿quién es el cliente y qué pidió?” y lo pinta. El primer pedido siempre es el mismo, para que todos practiquen igual: slime rosa, viscosidad alta, brillo. Eso está escrito en game_state, en new_order. Los pedidos siguientes salen al azar.
>
> El cliente es una foto PNG, no un muñequito 3D. El botón Manual no es una sexta hoja. Solo le dice al director: “abre el folleto encima”. El reloj se pausa para que puedas leer las fórmulas sin que te resten puntos.

Clic en Manual, muéstralo, ciérralo.

### BUILD — la receta

**Mostrar:** BUILD. Mueve un slider. Luego `build_station.py` y `game_state.update_recipe`.

> Aquí hay tres palancas. Polímero es el polvo que da cuerpo, como harina. Agente es lo que entrecruza, como gelatina: hace red y el slime se siente más gel. Velocidad es qué tan rápido gira el batidor, en RPM: revoluciones por minuto.
>
> Cuando arrastras una palanca, BUILD no se guarda el número para ella solita. Llama a update_recipe y lo escribe en la libreta. La calculadora todavía no pone la nota. Solo, si quieres, puede decir qué tan lleno se ve el vaso. Eso es dibujo, no puntaje.
>
> El colorante también se guarda en la libreta. Confirmar formulación es como decir “ya no toco la receta”. Pone un sí en confirmed. Hasta que no confirmes, en MIX el batidor no gira.
>
> Ojo, esto le gusta al profesor: si después de confirmar vuelves y mueves un slider, la libreta dice “esto ya no es la misma receta” y borra la mezcla. No puedes hacer trampa cambiando números a escondidas.

Confirma la formulación. Avisa en voz alta: “ya está el sí en la libreta”.

### MIX — el corazón de la ciencia

**Mostrar:** MIX. Luego `mix_station.py` `update` y `physics_engine.py` `viscosidad_en_tiempo`.

> MIX es la única hoja que usa de verdad el reloj de cada fotito. Si confirmaste y no has detenido, cada vueltita suma un poquito de tiempo, le pregunta a la calculadora “¿qué tan espeso voy?” y guarda un puntito para la gráfica azul.
>
> La gráfica de la izquierda es la importante. Imaginen un termómetro del espesor.
>
> La franja verde no es tu receta. Es lo que pidió el cliente. “Quiero el slime entre tanto y tanto”.
>
> La línea de puntitos es el tope de TU receta. Si nunca detienes, el slime se acerca a esa raya y se queda. No la cruza. Es como calentar agua: sube hacia una temperatura y se queda, no se pone más caliente que el fuego.
>
> La línea azul eres tú ahora. Empieza abajo y se curva hacia los puntitos.
>
> La barrita de abajo no es la nota. Es “qué tan cerca estoy del tope de mi receta”. Puedes llenarla y igual perder, si tu tope está fuera del verde. Y puedes detener a medias y sacar cien, si en ese momento la azul está dentro del verde.
>
> La gráfica de la derecha no es un examen. Es un retrato de cómo se comporta el slime si agitaras más rápido o más lento. No suma puntos.
>
> Detener Mezcla (o la barra espaciadora) copia el espesor de ahora y lo congela. La nota usa ese número congelado, no el tope. Si te pasas, puedes Reiniciar mezcla y volver a batir.

Detén cuando la azul esté en el verde. Di el número que salga.

### TOP — los stickers

**Mostrar:** TOP y `top_station.py` `_deliver`.

> Aquí la libreta tiene una cajita de stickers puestos. Clic en una herramienta la pone o la quita. También puedes arrastrarla al vaso. El brillo, las estrellas, la tapa, el sello y la etiqueta de seguridad son adornos. Si el cliente pidió brillo y no se lo pones, te faltan puntos. Si pones extras que no pidió, también te restan un poquito.
>
> Entregar Pedido es el portero. Revisa tres cosas: ¿confirmaste la receta? ¿detuviste la mezcla? ¿elegiste color? Si falta algo, sale un avisito amarillo y no te deja pasar. Si está bien, le pide a la calculadora el reporte, suma monedas en la libreta y el director cambia current a result.

Entrega el pedido.

### RESULT — la nota

**Mostrar:** RESULT y `result_station.py`.

> Esta hoja lee last_report, o sea “el último reporte”, que la calculadora escribió en la libreta. Pinta puntos de color, de viscosidad, de adornos, el total y las monedas.
>
> La cara del cliente cambia: triste si sacaste menos de setenta, normal si vas bien, más sonrisa y confeti si llegas a noventa.
>
> Nuevo Pedido llama a next_order: limpia la receta, pide otro cliente y vuelve a la hoja ORDER. Desde aquí no puedes volver a MIX a escondidas.

---

## 6. La calculadora, con palabras de cocina (3 min)

**Mostrar:** `physics_engine.py` y `settings.py`.

> Tres ideas. Nada de asustarse con las letras griegas.
>
> Primera: dilución. Si echas más “agua”, el polvo se reparte. El agente también ocupa espacio, así que aclara un poquito, pero a la vez entrecruza y le da más cuerpo. La frase es: concentración final igual a polímero por diez, dividido entre el volumen total.
>
> Segunda: el slime no es miel normal. La miel espesa igual si la revuelves despacio o rápido. Este slime es pseudoplástico: cuanto más rápido lo bates, más flojo se siente. Por eso, si el cliente pide viscosidad alta, no pongas el batidor al máximo. Más RPM baja el tope.
>
> Tercera: el espesor no aparece de golpe. Sube hacia el tope, como el agua hacia la temperatura del fuego. Por eso la azul nunca cruza los puntitos. Eso no es un bug. Es el modelo.
>
> Receta fácil para el profesor: viscosidad alta, más polímero, más agente, pocas RPM, y detener cuando la azul entre en el verde. Viscosidad baja: lo contrario, y un poco más de batido.

---

## 7. Cómo se saca la nota (1 min 30 s)

**Mostrar:** `calcular_puntuaciones` en `physics_engine.py`.

> Color: cincuenta o cero. Acertaste el colorante o no.
>
> Viscosidad: hasta cincuenta. Si caíste dentro de la banda del cliente, entre treinta y seis y cincuenta, mejor si quedaste cerca del centro. Si te saliste, como mucho treinta.
>
> Adornos: hasta diez. Te restan dos por cada sticker de más.
>
> Tiempo: dos minutos de gracia. Luego menos dos puntos cada ocho segundos, máximo menos dieciséis. Eso no se escribe en la tarjetita, pero sí se resta.
>
> Al final, si la suma pasa de cien, se deja en cien. Por eso a veces ves cincuenta más cuarenta y cuatro más diez y el total igual es cien: ciento cuatro no cabe.

---

## 8. Preguntas cortas (por si el profesor para el video)

Léelas solo si hace falta, o déjalas al final.

**¿Es como una página web con frontend y backend?**  
> No. Todo es un solo programa en tu computadora. La “cara” son las pantallas y los crayones. El “cerebro” son la libreta y la calculadora.

**¿Es MVC?**  
> Parecido, sin framework. Vista: screens y ui. Modelo: game_state y physics. Controlador: main y los clics.

**¿Por qué no Unity?**  
> Queríamos que las fórmulas se leyeran en un archivo de Python, no escondidas en un motor de videojuegos.

**¿El slime es física de partículas de verdad?**  
> No. El vaso anima olas y burbujas para que se vea más o menos espeso. La ciencia está en los números de μ, no en cada gotita.

**¿Por qué la curva no cruza la punteada?**  
> Porque el espesor se acerca al tope y se queda. La franja verde es otra cosa: es el pedido del cliente.

**¿Se puede hacer trampa?**  
> Si mueves sliders, se borra la mezcla. Si ya viste la nota, no te deja volver. Hay que hacer Nuevo Pedido.

**¿Hay sonido?**  
> El botón del parlante existe, pero todavía no hay audio.

**¿Dónde arranca todo?**  
> main.py, hasta abajo: if name igual main. Eso significa: “si me abriste a mí, enciende el juego”.

---

## 9. Cierre (30 s)

**Mostrar:** otra vez el Explorador, los cuatro oficios.

> En una frase, para que se les quede:
>
> El director elige la hoja. Las hojas dibujan y oyen los clics. La libreta recuerda el pedido y lo que tú hiciste. La calculadora saca el espesor y la nota. Los crayones y las fotos solo se ven.
>
> Si alguien pregunta “¿dónde está X?”, vamos al oficio que le toca. No mezclamos. Eso es cómo se conecta Slime Lab.
>
> Gracias.

---

## Extra: mapa para señalar con el mouse (imprímelo o tenlo al lado)

```
Tú haces clic
        ↓
main.py (el director) decide: ¿fue el menú o la hoja?
        ↓
la hoja (screens/...) atiende el clic
        ↓
escribe o lee game_state.py (la libreta)
        ↓
si necesita un número de espesor o la nota,
pregunta a physics_engine.py (la calculadora)
        ↓
physics lee settings.py (el recetario de números)
        ↓
la hoja pide a ui_components.py y assets_loader.py
que pinten vaso, botones y fotos
        ↓
main.py pinta las barras y muestra la fotito
```

Frase de bolsillo si se te olvida el guion:

> Cinco hojas, una libreta, una calculadora, un director que da vuelta las páginas sesenta veces por segundo.
