# Data Model: Backend autenticado de App 2

El servicio no persiste usuarios, tokens ni planes. Las entidades siguientes describen solo los valores de entrada, autorización y respuesta durante una solicitud.

## Solicitud de itinerario

| Campo | Tipo lógico | Validación |
|---|---|---|
| `ciudad` | Texto | Recortar espacios externos; longitud de 1 a 80 caracteres. |
| `fecha` | Fecha de calendario | ISO `YYYY-MM-DD`; no puede ser anterior a la fecha actual del servidor. |
| `personas` | Entero | Entre 1 y 20, inclusive. |
| `gustos` | Texto | Recortar espacios externos; longitud de 1 a 200 caracteres. |
| `Authorization` | Credencial Bearer | Requerida para `POST /api/plan`; no forma parte del JSON ni de la respuesta. |

Una solicitud no autenticada se rechaza antes de parsear o validar los campos JSON. Una solicitud autenticada pero inválida no llama a la IA.

## Token de sesión Clerk

| Atributo validado | Regla |
|---|---|
| Firma | Firma JWT RS256 validada con una clave pública obtenida del JWKS configurado. |
| `iss` | Debe coincidir con `CLERK_ISSUER`. |
| `exp` | Obligatorio y no caducado al validar. |
| `aud` | Se valida contra `CLERK_AUDIENCE` solo si dicha variable está definida y no vacía. |
| Estado | No válido/caducado produce 401 `NO_AUTENTICADO`; nunca autoriza la llamada de IA. |

El identificador del usuario, si aparece en claims, no se almacena ni se necesita para este endpoint.

## Itinerario

Respuesta correcta HTTP 200: objeto con `resultado` como texto plano. Debe contener, en ese orden y una sola vez, las franjas `Mañana:`, `Tarde:` y `Noche:`. No incluye tokens ni configuración del backend.

## Error de API

Respuesta de error: HTTP status apropiado y objeto `error` con:

| Campo | Regla |
|---|---|
| `codigo` | Código estable: `NO_AUTENTICADO`, `IA_NO_DISPONIBLE`, `IA_TIMEOUT` o `ERROR_INTERNO`. El `422` **no** lleva sobre `error` (se devuelve el `detail` de FastAPI, como en la App 1). |
| `mensaje` | Texto seguro y no sensible, sin stack trace, token, clave, ni detalle interno de proveedores. |

Estados definidos: 401 para autenticación, 422 para entrada inválida (cuerpo `detail` de FastAPI, igual que App 1), 502 para indisponibilidad de IA/formato generado inválido, 504 para timeout de IA y 500 para fallos internos inesperados.
