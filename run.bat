@echo off
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
