"""Sanear los datos de entrada y comprobar el formato del plan (prueba S18).

Este módulo vive aparte a propósito: reúne lo nuevo en un fichero propio para
no tocar el código del resto del equipo. ia.py solo llama a estas dos
funciones (dos líneas al principio y dos al final, sin borrar nada).

1. sanear_dato: lo que el usuario escribe no puede partir el prompt ni escribir
   una etiqueta del formato («Mañana:», «Tarde:», «Noche:»).
2. comprobar_plan: si la IA no ha escrito el plan de las tres líneas (una
   inyección de prompt puede hacer que devuelva cualquier cosa), no se
   devuelve: la API contesta 502 y no se pinta nada.
"""

import re  # para sanear los datos y buscar las etiquetas del formato

# El frontend parte la respuesta por estas tres etiquetas para repartir el
# plan en tres tarjetas: deben aparecer en este orden y UNA sola vez cada una.
ETIQUETAS = ["mañana", "tarde", "noche"]

# El prompt pide menos de 250 palabras. Este tope es el doble: corta salidas
# absurdas sin arriesgar un 502 a un plan legítimo.
MAX_PALABRAS = 500

# Busca «Mañana:», «Tarde:» o «Noche:», también en minúscula y con espacios
# antes de los dos puntos. Es el mismo criterio que usa el frontend.
ETIQUETAS_FORMATO = re.compile(r"\b(mañana|tarde|noche)\s*:", re.IGNORECASE)


def sanear_dato(valor: str) -> str:
    """Prepara un dato del usuario antes de meterlo en el prompt.

    - Un salto de línea rompería el bloque de datos y permitiría inyectar una
      línea nueva con apariencia de instrucción.
    - «Mañana:» escrito por el usuario se confundiría con una etiqueta del
      formato y el frontend contaría más de tres tarjetas.
    """
    # " ".join(valor.split()) quita saltos de línea y espacios sobrantes.
    return ETIQUETAS_FORMATO.sub(r"\1", " ".join(valor.split()))


def comprobar_plan(texto: str):
    """Devuelve None si el texto es un plan válido, o el motivo por el que no.

    La comprobación es deliberadamente laxa en lo accesorio (admite
    introducción, minúsculas y espacios de sobra) y estricta en lo que el
    frontend necesita: las tres etiquetas, en orden y sin repetir.
    """
    # El plan es texto plano: una etiqueta HTML o un bloque de código markdown
    # significa que la IA ha dejado de seguir el formato.
    if re.search(r"</?[a-zA-Z][^>]*>|```", texto):
        return "la respuesta contiene marcado HTML o Markdown"

    encontradas = [m.group(1).lower() for m in ETIQUETAS_FORMATO.finditer(texto)]
    if encontradas != ETIQUETAS:
        return f"las etiquetas del formato no están en orden: {encontradas}"

    if len(texto.split()) > MAX_PALABRAS:
        return f"el plan tiene más de {MAX_PALABRAS} palabras"

    return None
