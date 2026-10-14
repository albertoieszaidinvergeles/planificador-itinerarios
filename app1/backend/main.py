"""Backend de App 1: API del planificador de itinerarios.

Expone un único endpoint, POST /api/plan, que recibe los datos del
formulario, hace una llamada a la IA y devuelve el plan en JSON.
"""

# FastAPI
from fastapi import FastAPI # crea la API y gestiona las peticiones HTTP

from pydantic import BaseModel # para describir y validar los datos de entrada

# Función que habla con OpenRouter. Está en ia.py, separada
# para poder sustituirla por un mock en los tests (H3).
from ia import consultar_ia

# Crea la aplicación. uvicorn (y Vercel) buscan una variable llamada "app".
app = FastAPI(title="Planificador de itinerarios")


class Entrada(BaseModel):
    """Datos que envía el formulario (contrato de POST /api/plan).

    H1: solo se comprueban los tipos de cada campo.
    Los límites se añaden en H2.
    """

    ciudad: str
    fecha: str
    personas: int
    gustos: str


@app.post("/api/plan")
def crear_plan(entrada: Entrada) -> dict:
    """Recibe la entrada, consulta la IA una sola vez y devuelve el resultado."""
    # Cuando se llega aquí, FastAPI ya ha convertido el JSON de la petición
    # en un objeto Entrada. Si faltaba un campo o un tipo era incorrecto,
    # FastAPI ya habrá respondido 422 y esta función ni se ejecuta.
    texto = consultar_ia(
        entrada.ciudad, entrada.fecha, entrada.personas, entrada.gustos
    )

    # Se devuelve solo el texto, envuelto como dice el contrato: {"resultado": "..."}.
    # Nunca la respuesta completa de OpenRouter con sus metadatos.
    return {"resultado": texto}