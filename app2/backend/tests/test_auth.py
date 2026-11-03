from datetime import datetime, timedelta, timezone

import pytest

import auth


ISSUER = "https://issuer.test"


@pytest.fixture(autouse=True)
def configuracion_clerk(monkeypatch):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.delenv("CLERK_AUDIENCE", raising=False)


def test_token_firmado_por_jwks_valido(pares_rsa, crear_token, simular_jwks):
    token = crear_token(pares_rsa[0])

    claims = auth.verify_session_token(token)

    assert claims["iss"] == ISSUER
    assert claims["sub"] == "user_test"


def test_firma_de_otra_clave_se_rechaza(pares_rsa, crear_token, simular_jwks):
    token = crear_token(pares_rsa[1])

    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token)


def test_kid_no_publicado_se_rechaza(pares_rsa, crear_token, simular_jwks):
    token = crear_token(
        pares_rsa[0], headers={"kid": "clave-desconocida", "alg": "RS256"}
    )

    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token)


def test_issuer_incorrecto_se_rechaza(pares_rsa, crear_token, simular_jwks):
    token = crear_token(pares_rsa[0], iss="https://otro-issuer.test")

    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token)


def test_expiracion_vencida_se_rechaza(pares_rsa, crear_token, simular_jwks):
    token = crear_token(
        pares_rsa[0],
        exp=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token)


def test_claim_exp_es_obligatorio(pares_rsa, crear_token, simular_jwks):
    token = crear_token(pares_rsa[0], exp=None)

    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token)


def test_audiencia_se_valida_si_esta_configurada(
    pares_rsa, crear_token, simular_jwks, monkeypatch
):
    monkeypatch.setenv("CLERK_AUDIENCE", "app_test")
    token = crear_token(pares_rsa[0], aud="app_test")

    assert auth.verify_session_token(token)["aud"] == "app_test"

    token_incorrecto = crear_token(pares_rsa[0], aud="otra_app")
    with pytest.raises(auth.AuthenticationError):
        auth.verify_session_token(token_incorrecto)


def test_audiencia_no_se_exige_si_no_esta_configurada(
    pares_rsa, crear_token, simular_jwks, monkeypatch
):
    monkeypatch.delenv("CLERK_AUDIENCE", raising=False)
    token = crear_token(pares_rsa[0], aud="cualquier_audiencia")

    assert auth.verify_session_token(token)["aud"] == "cualquier_audiencia"


@pytest.mark.parametrize(
    "authorization",
    [None, "", "Basic token", "Bearer", "Bearer token con-espacios"],
)
def test_bearer_ausente_o_malformado_se_rechaza(authorization):
    with pytest.raises(auth.AuthenticationError):
        auth.bearer_token(authorization)


def test_url_jwks_por_defecto(pares_rsa, crear_token, jwks_publico, monkeypatch):
    urls = []
    monkeypatch.setattr(
        "auth._descargar_jwks",
        lambda url: (urls.append(url), jwks_publico["keys"])[1],
    )

    auth.verify_session_token(crear_token(pares_rsa[0]))

    assert urls == ["https://api.clerk.com/v1/jwks"]


def test_url_jwks_se_puede_configurar(
    pares_rsa, crear_token, jwks_publico, monkeypatch
):
    monkeypatch.setenv("CLERK_JWKS_URL", "https://ejemplo.test/jwks")
    urls = []
    monkeypatch.setattr(
        "auth._descargar_jwks",
        lambda url: (urls.append(url), jwks_publico["keys"])[1],
    )

    auth.verify_session_token(crear_token(pares_rsa[0]))

    assert urls == ["https://ejemplo.test/jwks"]
