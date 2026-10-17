import os
from datetime import date
import httpx

import formato  # saneado de datos y comprobación del formato del plan (S18)
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
    # S18 (solo se añade, no se toca lo de abajo): los datos del usuario se
    # sanean ANTES de entrar en el prompt. Un salto de línea serviría para
    # inyectar una línea nueva con apariencia de instrucción, y una
    # «Mañana:» escrita a mano se confundiría con una etiqueta del formato.
    ciudad = formato.sanear_dato(ciudad)
    gustos = formato.sanear_dato(gustos)

    # Construimos el prompt con los datos del formulario.
    #    {fecha} se convierte solo a texto con el formato AAAA-MM-DD.
    #    El frontend parte la respuesta por "Mañana:", "Tarde:" y "Noche:"
    #    para pintar tres tarjetas: por eso se le da a la IA el formato exacto.
    prompt = (
        f"Eres un asistente de viajes. Propón un plan para UN solo día en {ciudad} "
        f"el {fecha}, para {personas} persona(s) a las que les gusta: {gustos}.\n"
        "Usa exactamente este formato: tres líneas, una por franja, y cada "
        "etiqueta UNA sola vez. Escribe las dos o tres actividades de cada "
        "franja en la misma línea, separadas por punto y coma, y empieza "
        "con mayúscula:\n"
        "Mañana: Primera actividad; segunda actividad; tercera actividad\n"
        "Tarde: Primera actividad; segunda actividad; tercera actividad\n"
        "Noche: Primera actividad; segunda actividad; tercera actividad\n"
        "No escribas introducción ni despedida, y no uses las palabras "
        "mañana, tarde o noche seguidas de dos puntos en ningún otro sitio.\n"
        "Responde en español, en texto plano (sin HTML ni Markdown) "
        "y en menos de 250 palabras. No indiques el número de palabras."
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
    
    # S18 (solo se añade): comprobamos que la respuesta es un plan de verdad.
    # Si la IA obedeciera una inyección de prompt y no devolviera las tres
    # líneas, no se pinta nada: IAError se traduce en un 502 con la forma
    # del contrato. El motivo se queda en el servidor (en el log de uvicorn).
    if (motivo := formato.comprobar_plan(texto.strip())) is not None:
        raise IAError(motivo)

    return texto.strip() # Se devuelve el texto