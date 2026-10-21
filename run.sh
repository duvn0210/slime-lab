#!/bin/bash
# run.sh — Ubuntu/WSL: corre el juego con el Python del .venv (no el del sistema).
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Falta el entorno. Desde esta carpeta:"
  echo "  uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt"
  exit 1
fi
exec .venv/bin/python main.py
