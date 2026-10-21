"""
screens/ — paquete de las 5 estaciones (las “interfaces” del juego).

Para qué sirve:
    En Python, una carpeta con __init__.py es un paquete. Así main.py puede hacer:
        from screens.order_station import OrderStation

Archivos de este paquete:
    base_screen.py     clase padre + helpers de texto
    order_station.py   ORDER  (pedido)
    build_station.py   BUILD  (sliders y color)
    mix_station.py     MIX    (gráficas y detener)
    top_station.py     TOP    (adornos y entregar)
    result_station.py  RESULT (nota)

Conectado con:
    main.py crea las 5 clases y guarda un dict screens[nombre].
    Cada estación recibe la app (self) y por BaseScreen accede a state, physics y assets.
"""
