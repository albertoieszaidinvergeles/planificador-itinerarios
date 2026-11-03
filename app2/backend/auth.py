import json
import logging
import os
import time
from typing import Any

import httpx
import jwt

logger = logging.getLogger(__name__)

# JWKS por defecto: la API backend de Clerk (la Frontend API ya no publica
# /.well-known/jwks.json en el emisor de la instancia).
DEFAULT_JWKS_URL = "https://api.clerk.com/v1/jwks"

# Cache de claves JWKS (evita una llamada a la API por cada petición).
_JWKS_TTL_SECONDS = 3600
_JWKS_CACHE: dict[str, Any] = {"keys": None, "fetched_at": 0.0}


class AuthenticationError(Exception):
    """A session token is missing or cannot be verified."""

    def __init__(
        self,
        message: str = "Invalid Clerk session token.",
        reason: str = "invalid_token",
    ):
        super().__init__(message)
        self.reason = reason


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
        raise AuthenticationError(
            "Clerk JWKS does not contain any key.", reason="jwks_empty"
        )
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
        raise AuthenticationError(reason="jwks_key_id_not_found")
    if len(claves) == 1:
        return claves[0]
    raise AuthenticationError(reason="jwks_key_id_missing")


def verify_session_token(token: str) -> dict[str, Any]:
    issuer = os.getenv("CLERK_ISSUER", "").strip()
    if not issuer:
        raise AuthenticationError(
            "Clerk issuer is not configured.", reason="issuer_not_configured"
        )

    audience = os.getenv("CLERK_AUDIENCE", "").strip() or None

    try:
        headers = jwt.get_unverified_header(token)
        jwk = _buscar_clave(headers.get("kid"))
        signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    except AuthenticationError:
        raise
    except httpx.HTTPError as error:
        raise AuthenticationError(reason="jwks_fetch_failed") from error
    except jwt.PyJWTError as error:
        raise AuthenticationError(reason="invalid_token_header") from error
    except (ValueError, TypeError, KeyError) as error:
        raise AuthenticationError(reason="invalid_jwks_key") from error

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
    except jwt.ExpiredSignatureError as error:
        raise AuthenticationError(reason="token_expired") from error
    except jwt.InvalidIssuerError as error:
        raise AuthenticationError(reason="token_issuer_mismatch") from error
    except jwt.InvalidAudienceError as error:
        raise AuthenticationError(reason="token_audience_mismatch") from error
    except jwt.InvalidSignatureError as error:
        raise AuthenticationError(reason="token_signature_invalid") from error
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as error:
        raise AuthenticationError(reason="invalid_token") from error


def bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthenticationError(
            "Missing bearer token.", reason="missing_bearer_token"
        )

    scheme, separator, credentials = authorization.partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not credentials
        or credentials.strip() != credentials
        or " " in credentials
    ):
        raise AuthenticationError(
            "Invalid bearer token.", reason="invalid_bearer_header"
        )

    return credentials


def verify_bearer_token(authorization: str | None) -> dict[str, Any]:
    return verify_session_token(bearer_token(authorization))
