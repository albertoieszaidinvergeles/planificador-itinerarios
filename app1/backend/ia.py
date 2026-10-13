import os
import httpx

from dotenv import load_dotenv


load_dotenv() # Carga el env

# Configuración:
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "20")) # Timeout, Debe ser 20

URL_OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"

def consultar_ia(ciudad: str, fecha: str, personas: int, gustos: str) -> str:
    """Pide a la IA un plan de un día y devuelve el texto.

    Hace UNA sola llamada a la API de IA (regla del enunciado).
    """
    # Prompt con los datos del formulario.
    #    Pedimos texto plano porque el frontend lo mostrará tal cual, sin interpretar HTML.
    prompt = (
        f"Eres un asistente de viajes. Propón un plan para UN solo día en {ciudad} "
        f"el {fecha}, para {personas} persona(s) a las que les gusta: {gustos}.\n"
        "Organízalo en mañana, tarde y noche, con dos o tres actividades por franja.\n"
        "Responde en español, en texto plano (sin HTML ni Markdown) "
        "y en menos de 250 palabras."
    )
    # Petición a OpenRouter:
    respuesta = httpx.post(
        URL_OPENROUTER,
        headers={"Authorization": f"Bearer {AI_API_KEY}"}, # La cabecera, con la clave
        json={
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=AI_TIMEOUT,
    )

    # Para el control de excepciones:
    respuesta.raise_for_status()

    # Convertimos la respuesta JSON en un diccionario de Python:
    datos = respuesta.json()
    return datos["choices"][0]["message"]["content"]

# Prueba:
# if __name__ == "__main__":
#     print(consultar_ia("Granada", "2026-10-20", 2, "museos y tapas"))





