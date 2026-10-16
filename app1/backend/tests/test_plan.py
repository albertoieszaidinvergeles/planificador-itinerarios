"""Tests del backend de App 1 (H3).

La IA NUNCA se llama de verdad: se sustituye por funciones falsas (mocks).
Así los tests funcionan sin internet, sin clave y sin gastar cuota.
Se ejecutan con:  pytest -v   (desde app1/backend)
"""

from datetime import date, timedelta  # para fabricar fechas de hoy y de ayer
import httpx  # para fabricar el error de timeout de httpx (T08)

import pytest  # el framework de tests
from fastapi.testclient import TestClient  # hace peticiones a la API sin arrancar uvicorn

import ia  # lo necesitamos para bloquear la red (ia.httpx)
import main  # la API que probamos
from ia import IAError  # nuestro error de "la IA ha fallado" (T07)

# Cliente de pruebas: imita a un navegador que llama a nuestra API.
# raise_server_exceptions=False: si la API tiene un error inesperado,
# queremos recibir su respuesta 500, no que el test explote.
cliente = TestClient(main.app, raise_server_exceptions=False)

# Fecha de hoy en formato "AAAA-MM-DD" (hoy es una fecha válida).
HOY = date.today().isoformat()

# Texto fijo que devuelve la IA falsa: así sabemos exactamente qué esperar.
PLAN_FALSO = "Mañana: museo. Tarde: tapas. Noche: paseo."


def entrada_valida(**cambios) -> dict:
    """Devuelve un JSON válido. Con **cambios se sustituye algún campo.

    Ejemplo: entrada_valida(personas=0) -> igual que el válido pero con 0 personas.
    """
    datos = {"ciudad": "Sevilla", "fecha": HOY, "personas": 2, "gustos": "museos y tapas"}
    datos.update(cambios)  # pisa los campos indicados
    return datos


# --- Fixtures: preparación que pytest ejecuta antes de cada test ---


@pytest.fixture(autouse=True)
def bloquear_red(monkeypatch):
    """Red de seguridad (autouse = se aplica a TODOS los tests).

    Sustituye httpx.post por una función que falla: si algún test llegara
    a llamar a OpenRouter de verdad, no saldría ninguna petición.
    monkeypatch deshace el cambio al terminar cada test.
    """

    def prohibido(*args, **kwargs):
        raise AssertionError("Un test ha intentado llamar a la IA de verdad")

    monkeypatch.setattr(ia.httpx, "post", prohibido)


@pytest.fixture
def ia_falsa(monkeypatch):
    """Sustituye consultar_ia por una función falsa que apunta cada llamada.

    Devuelve la lista de llamadas: len(ia_falsa) dice cuántas veces se usó la "IA".
    """
    llamadas = []

    def falsa(ciudad, fecha, personas, gustos):
        llamadas.append((ciudad, fecha, personas, gustos))  # apunta la llamada
        return PLAN_FALSO  # responde al instante

    # Se cambia en "main", porque main.py hizo "from ia import consultar_ia"
    # y usa SU copia del nombre.
    monkeypatch.setattr(main, "consultar_ia", falsa)
    return llamadas


# --- T01-T06: validación de la entrada ---


def test_t01_entrada_valida(ia_falsa):
    """T01: datos correctos -> 200, el plan, y UNA sola llamada a la IA."""
    respuesta = cliente.post("/api/plan", json=entrada_valida())

    assert respuesta.status_code == 200
    assert respuesta.json() == {"resultado": PLAN_FALSO}
    assert len(ia_falsa) == 1


# parametrize: el mismo test se ejecuta una vez por cada valor de la lista.
@pytest.mark.parametrize("campo", ["ciudad", "gustos"])
def test_t02_texto_solo_espacios(ia_falsa, campo):
    """T02: un texto de solo espacios -> 422 y CERO llamadas a la IA."""
    # **{campo: "   "} equivale a escribir ciudad="   " o gustos="   ".
    respuesta = cliente.post("/api/plan", json=entrada_valida(**{campo: "   "}))

    assert respuesta.status_code == 422
    assert len(ia_falsa) == 0


@pytest.mark.parametrize("campo, maximo", [("ciudad", 80), ("gustos", 200)])
def test_t03_limite_exacto_se_acepta(ia_falsa, campo, maximo):
    """T03: justo en el máximo de caracteres -> se acepta (200)."""
    respuesta = cliente.post("/api/plan", json=entrada_valida(**{campo: "a" * maximo}))

    assert respuesta.status_code == 200


@pytest.mark.parametrize("campo, maximo", [("ciudad", 80), ("gustos", 200)])
def test_t04_limite_superado_se_rechaza(ia_falsa, campo, maximo):
    """T04: un carácter más del máximo -> 422 y sin llamada a la IA."""
    respuesta = cliente.post(
        "/api/plan", json=entrada_valida(**{campo: "a" * (maximo + 1)})
    )

    assert respuesta.status_code == 422
    assert len(ia_falsa) == 0


def test_t05_fecha_pasada(ia_falsa):
    """T05: fecha de ayer -> 422 señalando el campo fecha."""
    ayer = (date.today() - timedelta(days=1)).isoformat()
    respuesta = cliente.post("/api/plan", json=entrada_valida(fecha=ayer))

    assert respuesta.status_code == 422
    # detail[0]["loc"] dice qué campo falló: ["body", "fecha"].
    assert respuesta.json()["detail"][0]["loc"] == ["body", "fecha"]
    assert len(ia_falsa) == 0


@pytest.mark.parametrize("personas", [0, 21])
def test_t06_personas_fuera_de_rango(ia_falsa, personas):
    """T06: 0 y 21 personas -> 422 en ambos casos."""
    respuesta = cliente.post("/api/plan", json=entrada_valida(personas=personas))

    assert respuesta.status_code == 422
    assert len(ia_falsa) == 0


# --- T07-T09 y 500: errores de la IA y errores inesperados ---


def test_t07_fallo_del_proveedor(monkeypatch):
    """T07: la IA falla -> 502 con el error EXACTO del contrato (sin detalles internos)."""

    def falla(*args):
        raise IAError()  # lo mismo que hace ia.py cuando OpenRouter falla

    monkeypatch.setattr(main, "consultar_ia", falla)
    respuesta = cliente.post("/api/plan", json=entrada_valida())

    assert respuesta.status_code == 502
    # Comparamos el JSON COMPLETO: si se colara un stack trace o un
    # mensaje interno, ya no sería igual y el test fallaría.
    assert respuesta.json() == {
        "error": {
            "codigo": "IA_NO_DISPONIBLE",
            "mensaje": "No se ha podido completar la petición. Inténtalo más tarde.",
        }
    }


def test_t08_timeout_del_proveedor(monkeypatch):
    """T08: httpx agota el tiempo -> ia.py lanza IATimeout -> main.py responde 504.

    No esperamos 20 segundos de verdad: el mock lanza el timeout al instante.
    """

    def tarda_demasiado(*args, **kwargs):
        raise httpx.ReadTimeout("timeout simulado")  # el error real que da httpx

    # Aquí NO sustituimos consultar_ia: se ejecuta la de verdad,
    # solo cambiamos la petición a OpenRouter (httpx.post).
    monkeypatch.setattr(ia.httpx, "post", tarda_demasiado)
    respuesta = cliente.post("/api/plan", json=entrada_valida())

    assert respuesta.status_code == 504
    assert respuesta.json() == {
        "error": {
            "codigo": "IA_TIMEOUT",
            "mensaje": "La IA tardó demasiado. Inténtalo de nuevo.",
        }
    }


class RespuestaFalsa:
    """Imita una respuesta de httpx con código 200 y el JSON que queramos."""

    def __init__(self, datos):
        self.datos = datos  # el JSON que "devolverá" OpenRouter

    def raise_for_status(self):
        pass  # código 200: no hay error HTTP que lanzar

    def json(self):
        return self.datos


@pytest.mark.parametrize(
    "datos",
    [
        {},  # JSON sin "choices" -> KeyError
        {"choices": []},  # lista vacía -> IndexError
        {"choices": [{"message": {"content": "   "}}]},  # texto vacío
        {"choices": [{"message": {"content": None}}]},  # sin texto
    ],
)
def test_t09_respuesta_inesperada(monkeypatch, datos):
    """T09: OpenRouter responde 200 pero con basura -> 502, el contrato no se rompe."""
    # lambda: una función de una sola línea que devuelve la respuesta falsa.
    monkeypatch.setattr(ia.httpx, "post", lambda *args, **kwargs: RespuestaFalsa(datos))
    respuesta = cliente.post("/api/plan", json=entrada_valida())

    assert respuesta.status_code == 502
    assert respuesta.json()["error"]["codigo"] == "IA_NO_DISPONIBLE"


def test_error_inesperado_da_500(monkeypatch):
    """Un error que nadie previó -> 500 ERROR_INTERNO, sin contar qué ha pasado."""

    def rompe(*args):
        raise RuntimeError("fallo interno simulado")  # un error cualquiera

    monkeypatch.setattr(main, "consultar_ia", rompe)
    respuesta = cliente.post("/api/plan", json=entrada_valida())

    assert respuesta.status_code == 500
    assert respuesta.json() == {
        "error": {"codigo": "ERROR_INTERNO", "mensaje": "Error interno."}
    }
    

def test_prompt_pide_las_etiquetas_del_frontend(monkeypatch):
        """El prompt pide "Mañana:", "Tarde:" y "Noche:": el frontend parte el texto por ellas."""
        enviado = {}  # aquí guardaremos el cuerpo que se mandaría a OpenRouter
    
        def captura(url, **kwargs):
            # httpx.post(URL, headers=..., json=..., timeout=...): el prompt va en kwargs["json"].
            enviado.update(kwargs["json"])
            return RespuestaFalsa({"choices": [{"message": {"content": PLAN_FALSO}}]})
    
        monkeypatch.setattr(ia.httpx, "post", captura)
        respuesta = cliente.post("/api/plan", json=entrada_valida())
    
        assert respuesta.status_code == 200
        prompt = enviado["messages"][0]["content"]  # el texto que leería la IA
        for etiqueta in ("Mañana:", "Tarde:", "Noche:"):
            assert etiqueta in prompt


def test_cabeceras_de_seguridad(ia_falsa):
    """Las respuestas de la API llevan las cabeceras de seguridad (S14),
    tanto en el caso válido (200) como en un error de validación (422)."""
    for datos in (entrada_valida(), entrada_valida(personas=0)):
        respuesta = cliente.post("/api/plan", json=datos)

        for nombre, valor in main.CABECERAS_SEGURIDAD.items():
            assert respuesta.headers[nombre] == valor
        assert respuesta.headers["Content-Security-Policy"] == main.CSP_API