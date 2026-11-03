import urllib.request
from datetime import datetime, timedelta, timezone

import jwt
import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

import auth


@pytest.fixture(autouse=True)
def bloquear_red(monkeypatch):
    def prohibido(*args, **kwargs):
        raise AssertionError("Los tests no pueden acceder a la red")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", prohibido)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", prohibido)
    monkeypatch.setattr(urllib.request, "urlopen", prohibido)


@pytest.fixture(autouse=True)
def limpiar_cache_jwks(monkeypatch):
    """Cada test empieza sin JWKS cacheado en auth._JWKS_CACHE."""
    monkeypatch.setattr(auth, "_JWKS_CACHE", {"keys": None, "fetched_at": 0.0})


@pytest.fixture
def pares_rsa():
    return (
        rsa.generate_private_key(public_exponent=65537, key_size=2048),
        rsa.generate_private_key(public_exponent=65537, key_size=2048),
    )


@pytest.fixture
def crear_token():
    def crear(clave, headers=None, **cambios):
        ahora = datetime.now(timezone.utc)
        claims = {
            "iss": "https://issuer.test",
            "sub": "user_test",
            "iat": ahora,
            "exp": ahora + timedelta(minutes=5),
        }
        claims.update(cambios)
        return jwt.encode(
            claims,
            clave,
            algorithm="RS256",
            headers=headers or {"kid": "clave-prueba"},
        )

    return crear


@pytest.fixture
def jwks_publico(pares_rsa):
    jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        pares_rsa[0].public_key(), as_dict=True
    )
    jwk.update({"kid": "clave-prueba", "use": "sig", "alg": "RS256"})
    return {"keys": [jwk]}


@pytest.fixture
def simular_jwks(monkeypatch, jwks_publico):
    def instalar(jwks=None):
        contenido = jwks if jwks is not None else jwks_publico
        monkeypatch.setattr(
            "auth._obtener_claves_jwks",
            lambda: contenido["keys"],
        )

    instalar()
    return instalar
