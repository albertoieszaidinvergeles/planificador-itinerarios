# Research: Backend autenticado de App 2

## Decisiones

### Verificación de sesión Clerk

- **Decision**: Validar el Bearer token como JWT RS256 con PyJWT y resolver la clave pública mediante `PyJWKClient` desde `CLERK_ISSUER.rstrip("/") + "/.well-known/jwks.json"`. Exigir firma, `iss` coincidente y presencia de `exp` además de vigencia; pasar `audience` a la verificación solo cuando `CLERK_AUDIENCE` tenga valor y, en caso contrario, desactivar explícitamente la verificación de audiencia. Rechazar cualquier algoritmo distinto de RS256.
- **Rationale**: Coincide con FR-008 y evita aceptar tokens simplemente decodificados. Quitar una barra final al construir la URL evita una ruta con doble barra y no cambia el valor que debe coincidir con `iss`.
- **Alternatives considered**: Decodificar sin verificar firma (rechazado por seguridad); usar la secret key de Clerk como clave de firma (rechazado porque el contrato requiere las claves públicas JWKS); inferir issuer o URL JWKS de claims no verificados (rechazado).
- **Secret key**: `CLERK_SECRET_KEY` permanece exclusivamente en configuración privada del backend. No es una clave para verificar esta firma RS256 contra JWKS.
- **Clerk issuer**: La documentación oficial identifica `iss` con la URL Frontend API de la instancia y su JWKS con esa URL seguida de `/.well-known/jwks.json`; la comparación se hace contra la variable configurada, no contra un valor derivado del token.
- **Pruebas offline**: Crear una pareja RSA efímera y tokens firmados localmente; sustituir `PyJWKClient.fetch_data()` para devolver un JWKS estático en memoria que publique solo la clave pública esperada. Incluir clave distinta/no conocida, token sin `exp`, token caducado, issuer y audiencia erróneos.

### Autenticación antes de validar entrada

- **Decision**: Poner la autorización en una capa previa a la lectura/validación del modelo JSON para `POST /api/plan`, limitada a esa ruta. Omitir el preflight `OPTIONS`; mantener el control del orden con un test que envíe token ausente y cuerpo inválido simultáneamente y exija 401.
- **Rationale**: La spec exige prioridad observable del 401. Una dependencia de endpoint que se evalúe junto a validación automática del body podría no garantizar ese orden.
- **Alternatives considered**: Depender solo de una dependencia FastAPI del endpoint (rechazado si no garantiza precedencia sobre errores de parseo/validación del body).

### Errores de entrada

- **Decision**: Devolver el `422` **tal cual lo emite FastAPI** (`{"detail": [...]}`), idéntico a la App 1, sin sobre `error` ni código propio; los `401`, `502`, `504` y `500` sí usan `{"error": {"codigo": ..., "mensaje": ...}}` con los códigos y mensajes ya fijados.
- **Rationale**: La constitución (principio I) exige el mismo cuerpo de error que la App 1, que no define `codigo` en la validación. Así el frontend existente puede reutilizar su manejo de errores sin cambios ni adaptaciones.
- **Alternatives considered**: Normalizar el 422 a un sobre con código `VALIDACION` (rechazado: se desvía de la App 1, rompe la constitución I y obligaría al frontend de la App 2 a manejar dos formatos distintos).
- **Compatibilidad observada**: **Paridad literal conseguida**: el 422 de la App 2 es byte a byte el mismo que el de la App 1, así que los tests del contrato de la App 1 se pueden copiar sin adaptar.

### Dependencias Python

- **Decision**: Mantener las dependencias de ejecución y pytest en el único archivo permitido, `app2/backend/requirements.txt`. Usar las librerías ya aprobadas por la constitución: FastAPI, Pydantic vía FastAPI, httpx, python-dotenv y `PyJWT[crypto]`; incluir pytest para las pruebas locales.
- **Rationale**: Sigue el stack definido en la constitución y la restricción expresa del usuario de no añadir dependencias Python en otra ubicación.
- **Alternatives considered**: Crear `requirements-dev.txt` (descartado por la restricción); instalar paquetes durante este flujo (prohibido y no necesario para planificar).

### Generación segura y formato

- **Decision**: Mantener módulos separados de solicitud IA y saneado/verificación del resultado siguiendo el patrón probado de App 1. Sanear textos antes de insertarlos en el prompt, y comprobar que la salida presenta una sola etiqueta de cada franja, en orden y en texto plano; respuestas inutilizables se traducen a 502.
- **Rationale**: Reutiliza el comportamiento ya comprobado para los requisitos de inyección de prompt y presentación del itinerario, sin modificar App 1.
- **Alternatives considered**: Confiar exclusivamente en instrucciones del prompt (rechazado porque no garantiza formato seguro).

### CORS, documentación y cabeceras de seguridad

- **Decision**: Leer `CORS_ORIGINS` como lista separada por comas; permitir solo `POST`, `Content-Type` y `Authorization`, y dejar pasar preflight `OPTIONS`. Usar `DOCS_ACTIVOS=1` solo en local, con valor predeterminado apagado. Aplicar las mismas cabeceras y CSP de API que App 1.
- **Rationale**: `Authorization` es necesario para que el navegador envíe el token Clerk; el resto replica la configuración ya probada.
- **Alternatives considered**: Permitir todos los orígenes o encabezados (rechazado por ampliar innecesariamente la superficie de acceso); habilitar docs en producción (rechazado por FR-012).

### Fuentes oficiales consultadas

- Clerk, [Session tokens](https://clerk.com/docs/guides/sessions/session-tokens): issuer y claims de sesión.
- Clerk, [Manual JWT verification](https://clerk.com/docs/guides/sessions/manual-jwt-verification): verificación de JWKS y token.
- PyJWT, [Retrieve RSA signing keys from a JWKS endpoint](https://pyjwt.readthedocs.io/en/stable/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint): selección de clave pública por `kid`.
- PyJWT, [API reference for `jwt.decode`](https://pyjwt.readthedocs.io/en/stable/api.html#jwt.decode): algoritmos permitidos y opciones de validación.
- PyJWT, [Expiration time](https://pyjwt.readthedocs.io/en/stable/usage.html#expiration-time-claim-exp), [requiring claims](https://pyjwt.readthedocs.io/en/stable/usage.html#requiring-presence-of-claims) y [audience](https://pyjwt.readthedocs.io/en/stable/usage.html#audience-claim-aud): expiración, claims obligatorios y validación condicional de audiencia.
- pytest, [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html): sustitución local y temporal de comportamiento para aislar llamadas externas.

## Fuentes locales revisadas

- Constitución: `.specify/memory/constitution.md`.
- Especificación: `specs/001-backend-clerk-auth/spec.md`.
- Variables y placeholders existentes: `backend/.env.example`.
- Referencia de App 1 solo lectura: `app1/backend/main.py`, `ia.py`, `formato.py`, y `tests/test_plan.py` / `tests/test_formato.py`.

Las pruebas planificadas no acceden a estas fuentes en red ni consumen créditos. El runtime de Python exacto del despliegue no queda fijado en los archivos actuales de App 2; la implementación debe usar la versión que admita el runtime existente y ejecutar pytest en el `.venv` local.
