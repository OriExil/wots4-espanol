"""Rutas del proyecto. La copia del juego es de SOLO LECTURA.

El parcheador (parchear.py) indica otra carpeta de juego con la variable de entorno WOS4_JUEGO."""
import os
from pathlib import Path

PROYECTO = Path(__file__).resolve().parents[2]
if os.environ.get("WOS4_JUEGO"):
    JUEGO = Path(os.environ["WOS4_JUEGO"])
else:
    JUEGO = PROYECTO / "Way of the Samurai 4"      # equivale a ./juego_original/ (ver DECISIONES.md)
    if not JUEGO.exists():
        JUEGO = PROYECTO / "juego_original"
BUILD = PROYECTO / "build"
TRADUCCION = PROYECTO / "traduccion"
