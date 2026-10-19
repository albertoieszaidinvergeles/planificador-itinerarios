"""Punto de entrada del backend en Vercel (un solo proyecto para la App 1).

Vercel convierte cada fichero de `api/` en una función Python y la publica en
la ruta equivalente: **`api/plan.py` atiende a `/api/plan`**, que es la única
ruta que tiene la API. Así no hace falta ningún rewrite.

El resto del backend vive en `../backend` (`main.py`, `ia.py`, `formato.py`):
aquí solo se importa la app y se deja con el nombre `app`, que es el que busca
el runtime de Python. Las dependencias se instalan desde `app1/requirements.txt`.

Con `DOCS_ACTIVOS` sin definir (así está en Vercel) `/docs`, `/redoc` y
`/openapi.json` no se montan: quedan 404.

En local NADA de esto se usa: se sigue arrancando igual que siempre

    cd backend && uvicorn main:app --reload --no-server-header
"""

import os
import sys

# La función corre en api/; main.py está en ../backend. Sin esta línea
# "import main" no encontraría el módulo en Vercel.
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"),
)

# noqa: E402 — el import va DESPUÉS de añadir la ruta a propósito.
from main import app  # noqa: E402

# Es el nombre que el runtime de Python busca para servir la aplicación.
__all__ = ["app"]
