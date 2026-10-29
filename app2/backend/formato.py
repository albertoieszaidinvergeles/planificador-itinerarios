import re


ETIQUETAS = ["mañana", "tarde", "noche"]
MAX_PALABRAS = 500
ETIQUETAS_FORMATO = re.compile(r"\b(mañana|tarde|noche)\s*:", re.IGNORECASE)


def sanear_dato(valor: str) -> str:
    return ETIQUETAS_FORMATO.sub(r"\1", " ".join(valor.split()))


def comprobar_plan(texto: str) -> str | None:
    if re.search(r"</?[a-zA-Z][^>]*>|```", texto):
        return "la respuesta contiene marcado HTML o Markdown"

    encontradas = [
        match.group(1).lower() for match in ETIQUETAS_FORMATO.finditer(texto)
    ]
    if encontradas != ETIQUETAS:
        return f"las etiquetas del formato no están en orden: {encontradas}"

    if len(texto.split()) > MAX_PALABRAS:
        return f"el plan tiene más de {MAX_PALABRAS} palabras"

    return None
