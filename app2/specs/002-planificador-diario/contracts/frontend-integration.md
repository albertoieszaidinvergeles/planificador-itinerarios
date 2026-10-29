# Contrato de integración del frontend App 2

Este documento define cómo la pantalla única consume la autenticación y el endpoint ya existentes. No modifica ni amplía la API del backend. El contrato de referencia es [plan-api.md de App 2](../../001-backend-clerk-auth/contracts/plan-api.md).

## Interfaz de pantalla

- Una sola vista de planificación, sin rutas ni páginas propias de autenticación.
- Clerk ofrece acceso con Google en una ventana modal; una sesión activa muestra el control de usuario para cerrar sesión.
- Estados visibles: entrada, espera con indicador de carga, resultado y error.
- La acción principal se titula «Generar plan». Durante la espera queda deshabilitada y muestra «Generando…».
- Los campos ciudad, fecha, personas y gustos tienen etiquetas accesibles. Los errores de campo se asocian al control correspondiente; errores sin campo reconocido se muestran de forma general.
- La compañía es opcional, depende del número de personas y se incorpora al final de gustos. No aparece como campo del JSON.
- «Reintentar» vuelve a entrada, conserva los datos y no efectúa una petición.
- El resultado y los errores se muestran como texto literal; la salida de IA no se interpreta como HTML.

## Solicitud de planificación

- **Método y ruta**: `POST /api/plan`
- **URL**: `${VITE_API_BASE_URL}/api/plan` tras quitar barras finales de la base; si la base está vacía, `/api/plan` en el mismo origen.
- **Cabeceras**:

```http
Content-Type: application/json
Authorization: Bearer <token de sesión actual de Clerk>
```

- **JSON exacto**:

```json
{
  "ciudad": "Sevilla",
  "fecha": "AAAA-MM-DD",
  "personas": 2,
  "gustos": "museos y tapas (van con amigos)"
}
```

`gustos` contiene el texto de la persona y, si seleccionó compañía, el sufijo acordado. El cuerpo no contiene una clave separada `compania`. Antes de enviar, el frontend valida el texto final de gustos y el resto de las restricciones del contrato. Cada acción válida produce una sola solicitud; ausencia de sesión, validación fallida o estado de espera producen cero solicitudes adicionales.

## Respuestas y presentación

| HTTP | Cuerpo | Comportamiento del frontend |
|---:|---|---|
| 200 | `{"resultado":"..."}` | Presentar como texto; repartir en tarjetas Mañana/Tarde/Noche solo si se reconocen las tres etiquetas. Si falta alguna, mostrar el texto completo. Mostrar el aviso de contenido generado por IA y orientativo. |
| 401 | `{"error":{"codigo":"NO_AUTENTICADO","mensaje":"..."}}` | Solicitar iniciar sesión de nuevo; no repetir la petición automáticamente. |
| 422 | `{"detail":[...]}` | Asociar cada ubicación conocida a su campo y mostrar un mensaje general si hay algún error sin campo reconocido. No transformar el cuerpo del backend. |
| 500, 502, 504 | `{"error":{"codigo":"...","mensaje":"..."}}` | Mostrar un mensaje comprensible y habilitar «Reintentar» para volver a entrada sin perder datos y sin enviar automáticamente. |
| Fallo de red | Sin cuerpo legible | Mostrar el mensaje genérico de red; conservar el formulario y ofrecer recuperación sin reenvío automático. |

Ante una respuesta de éxito sin `resultado` de texto utilizable, mostrar un error recuperable y conservar el formulario.

## Variables de entorno

Solo se utilizan:

- `VITE_CLERK_PUBLISHABLE_KEY`: clave publicable de Clerk para inicializar el SDK en el navegador.
- `VITE_API_BASE_URL`: URL base del backend local durante desarrollo; vacía en producción para usar la ruta relativa del mismo origen.

No se incluye `CLERK_SECRET_KEY`, ninguna clave de IA ni ningún otro secreto en el frontend, el archivo de ejemplo o el bundle.

## Limitación conocida de desarrollo local

Cuando el frontend de desarrollo accede al backend en `127.0.0.1:8000`, la respuesta 401 actual puede carecer de cabeceras CORS. El navegador puede ocultar el estado HTTP y exponer un error de red a `fetch`; en ese caso se presenta el mensaje genérico de red requerido. No se cambia el backend ni se añade un proxy como parte de esta funcionalidad.
