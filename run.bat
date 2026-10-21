@echo off
REM run.bat — juega Slime Lab en Windows. Hay que estar EN la carpeta slime-lab.
REM Crea .venv con Python 3.12 si no existe. No uses el comando "python" a secas (puede ser 3.15).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno con Python 3.12...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Falta Python 3.12. En PowerShell corre: py install -y 3.12
    exit /b 1
  )
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" main.py
