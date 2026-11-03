import json
import os
import time
from typing import Any

import httpx
import jwt

# JWKS por defecto: la API backend de Clerk (la Frontend API ya no publica
# /.well-known/jwks.json en el emisor de la instancia).
DEFAULT_JWKS_URL = "https://api.clerk.com/v1/jwks"

# Cache de claves JWKS (evita una llamada a la API por cada petición).
_JWKS_TTL_SECONDS = 3600
_JWKS_CACHE: dict[str, Any] = {"keys": None, "fetched_at": 0.0}


class AuthenticationError(Exception):
    """A session token is missing or cannot be verified."""


def jwks_url() -> str:
    """URL del JWKS: CLERK_JWKS_URL si existe, si no el endpoint por defecto."""
    return os.getenv("CLERK_JWKS_URL", "").strip() or DEFAULT_JWKS_URL


def _descargar_jwks(url: str) -> list[dict[str, Any]]:
    """Descarga el JWKS de Clerk usando la clave secreta (Bearer)."""
    secret = os.getenv("CLERK_SECRET_KEY", "").strip()
    headers = {"Authorization": f"Bearer {secret}"} if secret else {}
    response = httpx.get(url, headers=headers, timeout=10.0)
    response.raise_for_status()
    keys = response.json().get("keys") or []
    if not keys:
        raise AuthenticationError("Clerk JWKS does not contain any key.")
    return keys


def _obtener_claves_jwks() -> list[dict[str, Any]]:
    """Claves JWKS vigentes, revalidando como máximo cada hora."""
    ahora = time.time()
    claves = _JWKS_CACHE["keys"]
    if claves and ahora - _JWKS_CACHE["fetched_at"] < _JWKS_TTL_SECONDS:
        return claves
    claves = _descargar_jwks(jwks_url())
    _JWKS_CACHE["keys"] = claves
    _JWKS_CACHE["fetched_at"] = ahora
    return claves


def _buscar_clave(kid: str | None) -> dict[str, Any]:
    """Devuelve el JWK de firma correspondiente al `kid` del token."""
    claves = _obtener_claves_jwks()
    if kid:
        for clave in claves:
            if clave.get("kid") == kid:
                return clave
        raise AuthenticationError("Invalid Clerk session token.")
    if len(claves) == 1:
        return claves[0]
    raise AuthenticationError("Invalid Clerk session token.")


def verify_session_token(token: str) -> dict[str, Any]:
    issuer = os.getenv("CLERK_ISSUER", "").strip()
    if not issuer:
        raise AuthenticationError("Clerk issuer is not configured.")

    audience = os.getenv("CLERK_AUDIENCE", "").strip() or None

    try:
        headers = jwt.get_unverified_header(token)
        jwk = _buscar_clave(headers.get("kid"))
        signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    except AuthenticationError:
        raise
    except (jwt.PyJWTError, ValueError, TypeError, KeyError, httpx.HTTPError) as error:
        raise AuthenticationError("Invalid Clerk session token.") from error

    try:
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience,
            options={
                "require": ["iss", "exp"],
                "verify_aud": audience is not None,
            },
        )
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as error:
        raise AuthenticationError("Invalid Clerk session token.") from error


def bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthenticationError("Missing bearer token.")

    scheme, separator, credentials = authorization.partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not credentials
        or credentials.strip() != credentials
        or " " in credentials
    ):
        raise AuthenticationError("Invalid bearer token.")

    return credentials


def verify_bearer_token(authorization: str | None) -> dict[str, Any]:
    return verify_session_token(bearer_token(authorization))
