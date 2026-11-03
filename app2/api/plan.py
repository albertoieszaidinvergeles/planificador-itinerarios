# api/plan.py  — Vercel serverless function (ASGI via Mangum)
# Vercel ejecuta este fichero como función Python independiente.
# Mangum envuelve la app FastAPI (ASGI) para que funcione en Lambda/Vercel.
import sys
import os

# Añade el directorio backend al path para poder importar main, auth, ia, formato
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from mangum import Mangum  # type: ignore[import-not-found]
from main import create_app  # type: ignore[import-not-found]

# En Vercel, mismo origen → CORS_ORIGINS vacío está bien.
# Las variables de entorno (CLERK_*, AI_*) se definen en el dashboard de Vercel.
_app = create_app()

# Vercel llama al handler con el evento Lambda estándar
handler = Mangum(_app, lifespan="off")

