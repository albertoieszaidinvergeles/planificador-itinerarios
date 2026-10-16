"""Backend de App 1: API del planificador de itinerarios.

Expone un único endpoint, POST /api/plan, que recibe los datos del
formulario, valida sus límites, hace una llamada a la IA y devuelve
el plan en JSON. Los errores siguen el contrato de la ERS.
"""

import os  # para leer variables de entorno (CORS_ORIGINS)
from datetime import date  # tipo de dato para fechas

from dotenv import load_dotenv  # carga el archivo .env
from fastapi import FastAPI, Request  # Request: datos de la petición (lo pide el manejador de errores)
from fastapi.middleware.cors import CORSMiddleware  # permite que el frontend llame a la API
from fastapi.responses import JSONResponse  # respuesta JSON con el código HTTP que elijamos
from pydantic import BaseModel, ConfigDict, Field, field_validator  # validación de la entrada

# Función que habla con OpenRouter y sus dos errores propios.
from ia import IAError, IATimeout, consultar_ia

# Cargamos el .env aquí también: así main.py no depende de que ia.py lo haga.
load_dotenv()

# --- /docs solo en local (prueba de seguridad S08) ---
# Swagger (/docs), ReDoc (/redoc) y el esquema (/openapi.json) explican la API
# entera a cualquiera. Solo se activan si DOCS_ACTIVOS=1 (en el .env local).
# En Vercel no se define la variable, así que esas rutas dan 404.
DOCS_ACTIVOS = os.getenv("DOCS_ACTIVOS", "0") == "1"

# Crea la aplicación. uvicorn (y Vercel) buscan una variable llamada "app".
app = FastAPI(
    title="Planificador de itinerarios",
    docs_url="/docs" if DOCS_ACTIVOS else None,  # None = esa ruta no existe
    redoc_url="/redoc" if DOCS_ACTIVOS else None,
    openapi_url="/openapi.json" if DOCS_ACTIVOS else None,
)

# --- CORS ---
# CORS_ORIGINS puede tener varias direcciones separadas por comas.
# split(",") las separa, strip() quita espacios y el "if" descarta las vacías.
ORIGENES = [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", "").split(",")
    if origen.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,  # solo estas webs pueden llamar a la API desde el navegador
    allow_methods=["POST"],  # nuestro único endpoint usa POST
    allow_headers=["Content-Type"],  # el frontend envía JSON
)

# --- Cabeceras de seguridad (prueba de seguridad S14) ---
# Instrucciones para el navegador que reducen ataques comunes.
CABECERAS_SEGURIDAD = {
    # No "adivinar" el tipo de contenido: si decimos JSON, es JSON.
    "X-Content-Type-Options": "nosniff",
    # Al salir hacia otra web, no enviar nuestra URL completa.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # La API no necesita cámara, micrófono, ubicación ni pagos.
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    # Usar siempre HTTPS (el navegador la ignora si llega por http, como en local).
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
}

# CSP muy estricta: la API solo devuelve JSON y no carga nada.
# Solo se aplica en /api/: en /docs bloquearía el JavaScript de Swagger.
CSP_API = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"


@app.middleware("http")
async def cabeceras_de_seguridad(request: Request, call_next):
    """Añade las cabeceras de seguridad a cada respuesta.

    Un middleware se ejecuta en TODAS las peticiones: deja pasar la petición
    (call_next), recibe la respuesta y le añade cabeceras antes de enviarla.
    Al declararse después de CORS, también cubre las respuestas de CORS.
    """
    respuesta = await call_next(request)  # la petición sigue su camino normal

    for nombre, valor in CABECERAS_SEGURIDAD.items():
        # setdefault: añade la cabecera solo si no existe (no pisa otras).
        respuesta.headers.setdefault(nombre, valor)

    if request.url.path.startswith("/api/"):
        respuesta.headers.setdefault("Content-Security-Policy", CSP_API)

    return respuesta


class Entrada(BaseModel):
    """Datos que envía el formulario (contrato de POST /api/plan)."""

    # Quita los espacios del principio y del final de todos los textos
    # ANTES de comprobar las longitudes: "   " queda en "" y da 422.
    model_config = ConfigDict(str_strip_whitespace=True)

    ciudad: str = Field(min_length=1, max_length=80)
    fecha: date  # Pydantic convierte "2026-10-20" en un objeto date (o da 422)
    personas: int = Field(ge=1, le=20)  # ge = mayor o igual, le = menor o igual
    gustos: str = Field(min_length=1, max_length=200)

    @field_validator("fecha")
    @classmethod
    def fecha_no_pasada(cls, valor: date) -> date:
        """Rechaza fechas anteriores a hoy (hoy sí vale)."""
        if valor < date.today():
            # Un ValueError aquí hace que FastAPI responda 422.
            raise ValueError("La fecha no puede ser anterior a hoy.")
        return valor


def respuesta_error(estado: int, codigo: str, mensaje: str) -> JSONResponse:
    """Construye un error con el formato del contrato: {"error": {"codigo", "mensaje"}}."""
    return JSONResponse(
        status_code=estado,
        content={"error": {"codigo": codigo, "mensaje": mensaje}},
    )


@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception) -> JSONResponse:
    """Cualquier error que no hayamos previsto: 500 sin dar detalles internos."""
    return respuesta_error(500, "ERROR_INTERNO", "Error interno.")


# Sin "-> dict": la función puede devolver un dict (200) o un JSONResponse (502/504).
@app.post("/api/plan")
def crear_plan(entrada: Entrada):
    """Recibe la entrada ya validada, consulta la IA una vez y devuelve el resultado."""
    try:
        texto = consultar_ia(
            entrada.ciudad, entrada.fecha, entrada.personas, entrada.gustos
        )
    # Traducimos nuestros errores a los códigos del contrato.
    except IATimeout:
        return respuesta_error(
            504, "IA_TIMEOUT", "La IA tardó demasiado. Inténtalo de nuevo."
        )
    except IAError:
        return respuesta_error(
            502,
            "IA_NO_DISPONIBLE",
            "No se ha podido completar la petición. Inténtalo más tarde.",
        )

    # Todo bien: solo el texto, como dice el contrato.
    return {"resultado": texto}