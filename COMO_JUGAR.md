# Cómo abrir Slime Lab en otro PC (Visual Studio)

El otro PC **sí necesita Visual Studio** (para mostrar y explicar el código). No hay que escribir comandos de `.venv` a mano.

## 1. Una vez en esa máquina

- Visual Studio con la carga **Python development**
- **Python 3.12** (no 3.14 ni 3.15: pygame no instala)

Si no está 3.12, en PowerShell:

```powershell
py install -y 3.12
```

O instálalo desde https://www.python.org/downloads/ y marca **Add python.exe to PATH**.

## 2. Clonar el repo

En Visual Studio: **Git → Clone Repository**

```
https://github.com/duvn0210/slime-lab.git
```

O en GitHub: **Code → Download ZIP** y extrae la carpeta.

## 3. Preparar el entorno (doble clic)

Entra a la carpeta `slime-lab` y **doble clic en `setup.bat`**.

Eso crea `.venv` e instala pygame. Espera a que diga **Listo**.

## 4. Correrlo desde Visual Studio

1. **File → Open → Folder** y elige `slime-lab` (no hace falta un `.sln`).
2. Elige el intérprete **`.venv\Scripts\python.exe`** (Python 3.12). Si eliges el `python` de 3.15, vuelve a fallar.
3. Clic derecho en `main.py` → **Set as Startup File**.
4. **F5**.

Para jugar sin depurar: doble clic en `run.bat`.

## Qué explicar en la presentación

El juego entra por `main.py`. Las estaciones están en `screens/`. Las fórmulas (dilución, ley de potencia, puntaje) están en `physics_engine.py`. El detalle pedagógico está en `DOCUMENTACION.md`.
