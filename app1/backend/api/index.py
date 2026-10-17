"""Punto de entrada del backend en Vercel.

Vercel convierte cada fichero de `api/` en una función Python. Nuestra app
FastAPI vive un nivel arriba (`main.py`, `ia.py`, `formato.py`), así que aquí
solo se importa y se deja con el nombre `app`, que es el que busca el runtime.

En local NADA de esto se usa: se sigue arrancando igual que siempre

    uvicorn main:app --reload --no-server-header
"""

import os
import sys

# La función se ejecuta desde api/; el resto del backend está un nivel arriba.
# Sin esto, "import main" no encontraría el módulo en Vercel.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# noqa: E402 — el import va DESPUÉS de añadir la ruta a propósito.
from main import app  # noqa: E402

# Es el nombre que el runtime de Python busca para servir la aplicación.
__all__ = ["app"]
