# Contract: `POST /api/plan`

## Alcance

Único endpoint de generación del backend App 2. El endpoint solo procesa solicitudes JSON después de autorizar una sesión Clerk.

## Solicitud

- Método y ruta: `POST /api/plan`
- Tipo de contenido: `application/json`
- Cabecera: `Authorization: Bearer <session-token>`
- JSON:

```json
{
  "ciudad": "Sevilla",
  "fecha": "YYYY-MM-DD",
  "personas": 2,
  "gustos": "museos y tapas"
}
```

| Campo | Regla |
|---|---|
| `ciudad` | Texto no vacío tras recortar espacios, máximo 80 caracteres. |
| `fecha` | Fecha ISO de hoy o futura. |
| `personas` | Entero entre 1 y 20 inclusive. |
| `gustos` | Texto no vacío tras recortar espacios, máximo 200 caracteres. |

## Respuestas

| Estado | Código | Cuerpo |
|---:|---|---|
| 200 | — | `{"resultado":"Mañana: ...\nTarde: ...\nNoche: ..."}` |
| 401 | `NO_AUTENTICADO` | `{"error":{"codigo":"NO_AUTENTICADO","mensaje":"..."}}` |
| 422 | — | `{"detail":[{"type":"...", "loc":["body","..."], "msg":"..."}]}` (idéntico a la App 1) |
| 502 | `IA_NO_DISPONIBLE` | `{"error":{"codigo":"IA_NO_DISPONIBLE","mensaje":"..."}}` |
| 504 | `IA_TIMEOUT` | `{"error":{"codigo":"IA_TIMEOUT","mensaje":"..."}}` |
| 500 | `ERROR_INTERNO` | `{"error":{"codigo":"ERROR_INTERNO","mensaje":"..."}}` |

Los mensajes concretos 401, 502, 504 y 500 mantienen el texto fijado por el contrato de App 1. El `422` **no lleva sobre `error`**: se devuelve tal cual lo emite la validación de FastAPI, exactamente igual que en la App 1, para que el frontend existente pueda reutilizar el mismo manejo sin cambios.

## Precedencia y seguridad

1. Rechazar credencial ausente o inválida con 401 antes de inspeccionar/validar el JSON y antes de llamar a la IA.
2. Verificar RS256 usando las claves públicas del JWKS derivado de `CLERK_ISSUER`; validar emisor y expiración, y audiencia solo si `CLERK_AUDIENCE` está configurada.
3. Validar los campos; los errores de entrada responden 422 y no llaman a la IA.
4. Generar y comprobar el formato; fallos del proveedor o salida inutilizable responden 502, timeout responde 504.
5. Fallos inesperados responden 500 sin detalles internos.

Todas las respuestas de `/api/` llevan las cabeceras de seguridad de App 1:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains`
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'`

El middleware CORS admite exclusivamente orígenes de `CORS_ORIGINS`, el método `POST`, los encabezados `Content-Type` y `Authorization`, y las solicitudes de preflight `OPTIONS`.

## Configuración de documentación

`/docs`, `/redoc` y `/openapi.json` existen solo con `DOCS_ACTIVOS=1`. En desarrollo local el `.env.example` documenta el valor `1`; en Vercel la variable no se define, por lo que las rutas quedan deshabilitadas.

## Nota de compatibilidad

El `422` **no se normaliza**: se devuelve el cuerpo `{"detail": [...]}` de FastAPI, idéntico al de la App 1, de modo que el contrato del endpoint es literalmente el de la App 1 **más** el `401 NO_AUTENTICADO` de Clerk. El frontend de App 2 puede reutilizar sin cambios el manejo de errores del frontend de App 1.
