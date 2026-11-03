from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import main


PLAN_FALSO = "Mañana: museo. Tarde: tapas. Noche: paseo."


def entrada_valida(**cambios):
    datos = {
        "ciudad": "Sevilla",
        "fecha": date.today().isoformat(),
        "personas": 2,
        "gustos": "museos y tapas",
    }
    datos.update(cambios)
    return datos


@pytest.fixture
def cliente(monkeypatch):
    def verificar_token(authorization):
        if authorization != "Bearer token-valido":
            raise main.auth.AuthenticationError()
        return {"sub": "user_test"}

    monkeypatch.setattr(main.auth, "verify_bearer_token", verificar_token)
    return TestClient(main.app, raise_server_exceptions=False)


def test_sin_token_precede_cuerpo_invalido_y_no_llama_ia(cliente, monkeypatch):
    llamadas = []
    monkeypatch.setattr(main, "consultar_ia", lambda *args: llamadas.append(args))

    respuesta = cliente.post("/api/plan", json={"personas": 0})

    assert respuesta.status_code == 401
    assert respuesta.json() == {
        "error": {
            "codigo": "NO_AUTENTICADO",
            "mensaje": main.MENSAJE_NO_AUTENTICADO,
        }
    }
    for nombre, valor in main.CABECERAS_SEGURIDAD.items():
        assert respuesta.headers[nombre] == valor
    assert respuesta.headers["Content-Security-Policy"] == main.CSP_API
    assert llamadas == []


def test_token_invalido_no_llama_ia(cliente, monkeypatch):
    def token_invalido(_header):
        raise main.auth.AuthenticationError()

    llamadas = []
    monkeypatch.setattr(main.auth, "verify_bearer_token", token_invalido)
    monkeypatch.setattr(main, "consultar_ia", lambda *args: llamadas.append(args))

    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"
    assert llamadas == []


def test_rechazo_de_sesion_se_registra_sin_incluir_el_token(
    cliente, monkeypatch, caplog
):
    token = "token-privado-de-prueba"

    def token_caducado(_authorization):
        raise main.auth.AuthenticationError(reason="token_expired")

    monkeypatch.setattr(main.auth, "verify_bearer_token", token_caducado)
    with caplog.at_level("WARNING", logger="main"):
        respuesta = cliente.post(
            "/api/plan",
            json=entrada_valida(),
            headers={"Authorization": f"Bearer {token}"},
        )

    assert respuesta.status_code == 401
    assert "reason=token_expired" in caplog.text
    assert "POST" in caplog.text
    assert "/api/plan" in caplog.text
    assert token not in caplog.text


def test_token_firmado_por_otra_clave_devuelve_401(
    monkeypatch, pares_rsa, crear_token, simular_jwks
):
    monkeypatch.setenv("CLERK_ISSUER", "https://issuer.test")
    token = crear_token(pares_rsa[1])
    llamadas = []
    monkeypatch.setattr(main, "consultar_ia", lambda *args: llamadas.append(args))
    cliente_real = TestClient(main.app, raise_server_exceptions=False)

    respuesta = cliente_real.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"
    assert llamadas == []


def test_solicitud_valida_devuelve_plan(cliente, monkeypatch):
    llamadas = []

    def ia_falsa(ciudad, fecha, personas, gustos):
        llamadas.append((ciudad, fecha, personas, gustos))
        return PLAN_FALSO

    monkeypatch.setattr(main, "consultar_ia", ia_falsa)
    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"resultado": PLAN_FALSO}
    posiciones = [
        respuesta.json()["resultado"].index(etiqueta)
        for etiqueta in ("Mañana:", "Tarde:", "Noche:")
    ]
    assert posiciones == sorted(posiciones)
    assert len(llamadas) == 1


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("ciudad", "   "),
        ("ciudad", "a" * 81),
        ("gustos", ""),
        ("gustos", "a" * 201),
        ("personas", 0),
        ("personas", 21),
        ("fecha", (date.today() - timedelta(days=1)).isoformat()),
        ("fecha", "no-es-fecha"),
    ],
)
def test_entrada_invalida_conserva_422_fastapi_y_no_llama_ia(
    cliente, monkeypatch, campo, valor
):
    llamadas = []
    monkeypatch.setattr(main, "consultar_ia", lambda *args: llamadas.append(args))

    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(**{campo: valor}),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 422
    assert set(respuesta.json()) == {"detail"}
    assert isinstance(respuesta.json()["detail"], list)
    assert llamadas == []


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("ciudad", "a"),
        ("ciudad", "a" * 80),
        ("gustos", "a"),
        ("gustos", "a" * 200),
        ("personas", 1),
        ("personas", 20),
        ("fecha", date.today().isoformat()),
        ("fecha", (date.today() + timedelta(days=1)).isoformat()),
    ],
)
def test_limites_validos_se_aceptan(cliente, monkeypatch, campo, valor):
    monkeypatch.setattr(main, "consultar_ia", lambda *args: PLAN_FALSO)

    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(**{campo: valor}),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 200


def test_error_ia_disponibilidad_mapea_a_502(cliente, monkeypatch):
    def ia_no_disponible(*_args):
        raise main.IAError()

    monkeypatch.setattr(main, "consultar_ia", ia_no_disponible)
    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 502
    assert respuesta.json() == {
        "error": {
            "codigo": "IA_NO_DISPONIBLE",
            "mensaje": "No se ha podido completar la petición. Inténtalo más tarde.",
        }
    }


def test_timeout_ia_mapea_a_504(cliente, monkeypatch):
    def ia_timeout(*_args):
        raise main.IATimeout()

    monkeypatch.setattr(main, "consultar_ia", ia_timeout)
    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 504
    assert respuesta.json() == {
        "error": {
            "codigo": "IA_TIMEOUT",
            "mensaje": "La IA tardó demasiado. Inténtalo de nuevo.",
        }
    }


def test_error_inesperado_mapea_a_500_sin_detalles(cliente, monkeypatch):
    def ia_rompe(*_args):
        raise RuntimeError("detalle interno que no debe filtrarse")

    monkeypatch.setattr(main, "consultar_ia", ia_rompe)
    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-valido"},
    )

    assert respuesta.status_code == 500
    assert respuesta.json() == {
        "error": {"codigo": "ERROR_INTERNO", "mensaje": "Error interno."}
    }
    assert "detalle interno" not in respuesta.text
    for nombre, valor in main.CABECERAS_SEGURIDAD.items():
        assert respuesta.headers[nombre] == valor
    assert respuesta.headers["Content-Security-Policy"] == main.CSP_API


def test_cabeceras_de_seguridad_en_respuesta_api(cliente, monkeypatch):
    monkeypatch.setattr(main, "consultar_ia", lambda *_args: PLAN_FALSO)

    respuesta = cliente.post(
        "/api/plan",
        json=entrada_valida(),
        headers={"Authorization": "Bearer token-valido"},
    )

    for nombre, valor in main.CABECERAS_SEGURIDAD.items():
        assert respuesta.headers[nombre] == valor
    assert respuesta.headers["Content-Security-Policy"] == main.CSP_API


def test_cors_permite_preflight_con_authorization():
    app = main.create_app(cors_origins=["https://frontend.test"], docs_activos=False)
    cliente_cors = TestClient(app, raise_server_exceptions=False)

    respuesta = cliente_cors.options(
        "/api/plan",
        headers={
            "Origin": "https://frontend.test",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "https://frontend.test"
    assert "authorization" in respuesta.headers["access-control-allow-headers"].lower()


def test_docs_solo_se_habilitan_con_flag_explicito():
    docs_off = TestClient(
        main.create_app(docs_activos=False), raise_server_exceptions=False
    )
    docs_on = TestClient(
        main.create_app(docs_activos=True), raise_server_exceptions=False
    )

    for ruta in ("/docs", "/redoc", "/openapi.json"):
        assert docs_off.get(ruta).status_code == 404
        assert docs_on.get(ruta).status_code == 200
