@echo off
cd /d "%~dp0"
echo === Slime Lab: preparando el entorno (una sola vez) ===

py -3.12 -c "import sys" >nul 2>&1
if errorlevel 1 (
  echo No esta Python 3.12. Intentando instalarlo...
  py install -y 3.12
  if errorlevel 1 (
    echo No se pudo instalar. Baja Python 3.12 de python.org y marca Add python.exe to PATH.
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando .venv con Python 3.12...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Fallo al crear el entorno.
    pause
    exit /b 1
  )
)

echo Instalando pygame...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Fallo pip. No uses Python 3.14/3.15; este juego va con 3.12.
  pause
  exit /b 1
)

echo.
echo Listo. Ahora en Visual Studio:
echo  1. File - Open - Folder - esta carpeta slime-lab
echo  2. Arriba a la derecha o en el pie, elige el interprete:
echo     .venv\Scripts\python.exe
echo  3. Clic derecho en main.py - Set as Startup File
echo  4. F5
echo.
echo Para jugar sin Visual Studio: doble clic en run.bat
pause
