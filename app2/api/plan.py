# api/plan.py — función Python de Vercel para POST /api/plan.
import sys
import os

# El backend vive en ../backend respecto a la raíz del proyecto Vercel.
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend",
    ),
)

# Vercel detecta la aplicación ASGI exportada con el nombre `app`.
from main import app  # noqa: E402

__all__ = ["app"]
