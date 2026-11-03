import logging
import os
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.responses import Response

import auth

logger = logging.getLogger(__name__)

load_dotenv()

CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
}
CSP_API = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"

# Fix 2: mensaje unificado entre 401 y doc técnico
MENSAJE_NO_AUTENTICADO = "Inicia sesión para continuar."


class IAError(Exception):
    """The AI provider failed or returned an unusable response."""


class IATimeout(Exception):
    """The AI provider did not respond before its timeout."""


class Entrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    ciudad: str = Field(min_length=1, max_length=80)
    fecha: date
    personas: int = Field(ge=1, le=20)
    gustos: str = Field(min_length=1, max_length=200)

    @field_validator("fecha")
    @classmethod
    def fecha_no_pasada(cls, valor: date) -> date:
        if valor < date.today():
            raise ValueError("La fecha no puede ser anterior a hoy.")
        return valor


def respuesta_error(estado: int, codigo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=estado,
        content={"error": {"codigo": codigo, "mensaje": mensaje}},
    )


def aplicar_cabeceras_seguridad(response: Response, path: str) -> None:
    for nombre, valor in CABECERAS_SEGURIDAD.items():
        response.headers.setdefault(nombre, valor)
    if path.startswith("/api/"):
        response.headers.setdefault("Content-Security-Policy", CSP_API)


def consultar_ia(ciudad: str, fecha: date, personas: int, gustos: str) -> str:
    from ia import consultar_ia as generar_plan

    return generar_plan(ciudad, fecha, personas, gustos)


def _origenes_cors() -> list[str]:
    return [
        origen.strip()
        for origen in os.getenv("CORS_ORIGINS", "").split(",")
        if origen.strip()
    ]


def create_app(
    cors_origins: list[str] | None = None,
    docs_activos: bool | None = None,
) -> FastAPI:
    if docs_activos is None:
        docs_activos = os.getenv("DOCS_ACTIVOS", "0") == "1"
    if cors_origins is None:
        cors_origins = _origenes_cors()

    app = FastAPI(
        title="Planificador de itinerarios",
        docs_url="/docs" if docs_activos else None,
        redoc_url="/redoc" if docs_activos else None,
        openapi_url="/openapi.json" if docs_activos else None,
    )

    # Fix 1: CORS debe envolver al middleware de auth para que los 401/500
    # también lleven Access-Control-Allow-Origin.
    # En Starlette el orden de add_middleware es LIFO: el último registrado
    # se ejecuta primero. Por eso registramos primero el middleware http
    # (auth + seguridad) y después CORSMiddleware, que así queda más externo.

    @app.middleware("http")
    async def seguridad_y_autenticacion(request: Request, call_next):
        # OPTIONS (preflight CORS) pasa sin autenticación
        if request.url.path == "/api/plan" and request.method == "POST":
            try:
                auth.verify_bearer_token(request.headers.get("authorization"))
            except auth.AuthenticationError as error:
                logger.warning(
                    "Authentication rejected: reason=%s method=%s path=%s",
                    error.reason,
                    request.method,
                    request.url.path,
                )
                response = respuesta_error(
                    401, "NO_AUTENTICADO", MENSAJE_NO_AUTENTICADO
                )
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)

        aplicar_cabeceras_seguridad(response, request.url.path)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.exception_handler(Exception)
    async def error_interno(request: Request, _exc: Exception) -> JSONResponse:
        response = respuesta_error(500, "ERROR_INTERNO", "Error interno.")
        aplicar_cabeceras_seguridad(response, request.url.path)
        return response

    @app.post("/api/plan")
    def crear_plan(entrada: Entrada):
        try:
            texto = consultar_ia(
                entrada.ciudad, entrada.fecha, entrada.personas, entrada.gustos
            )
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

        return {"resultado": texto}

    return app


app = create_app()
