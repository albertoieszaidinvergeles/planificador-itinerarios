import os
from datetime import date
import httpx

from dotenv import load_dotenv


load_dotenv() # Carga el env

# Configuración:
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "20"))

# Dirección del servicio de chat de OpenRouter
URL_OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"


# Errores propios del módulo:

class IAError(Exception):
    """La IA ha fallado o ha devuelto algo inutilizable (se traduce a 502)."""


class IATimeout(Exception):
    """La IA no ha respondido dentro de AI_TIMEOUT (se traduce a 504)."""


def consultar_ia(ciudad: str, fecha: date, personas: int, gustos: str) -> str:
    """Pide a la IA un plan de un día y devuelve el texto.

    Hace UNA sola llamada. Si algo falla, lanza IATimeout o IAError.
    """
    # Construimos el prompt con los datos del formulario.
    #    {fecha} se convierte solo a texto con el formato AAAA-MM-DD.
    prompt = (
        f"Eres un asistente de viajes. Propón un plan para UN solo día en {ciudad} "
        f"el {fecha}, para {personas} persona(s) a las que les gusta: {gustos}.\n"
        "Organízalo en mañana, tarde y noche, con dos o tres actividades por franja.\n"
        "Responde en español, en texto plano (sin HTML ni Markdown) "
        "y en menos de 250 palabras."
    )

    try:
        # Hacemos la petición a OpenRouter.
        respuesta = httpx.post(
            URL_OPENROUTER,
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "reasoning": {"enabled": False}, # Le pedimos al modelo que no razone antes de responder
            },
            timeout=AI_TIMEOUT,
        )

        # Si OpenRouter devuelve un código de error (401, 429, 500…), lanza excepción.
        respuesta.raise_for_status()

        # Sacamos el texto de la respuesta.
        datos = respuesta.json()
        texto = datos["choices"][0]["message"]["content"]

    # Traducimos los fallos a nuestros dos errores.
    #    TimeoutException es un tipo particular de HTTPError. Tiene que ir primero.
    except httpx.TimeoutException as error:
        raise IATimeout() from error
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as error:
        # HTTPError: códigos de error (429...) y fallos de conexión.
        # ValueError: la respuesta no es JSON válido.
        # KeyError/IndexError/TypeError: el JSON no tiene la forma esperada.
        raise IAError() from error

    # Respuesta inválida: No texto, o vacío.
    if not isinstance(texto, str) or not texto.strip():
        raise IAError()
    
    return texto.strip() # Se devuelve el texto