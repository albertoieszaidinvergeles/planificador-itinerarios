# Feature Specification: Backend autenticado de App 2

**Feature Branch**: No especificada

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: Implementar exclusivamente el backend de App 2 para generar itinerarios mediante `POST /api/plan`, replicar el contrato de App 1 y añadir autenticación de sesión Clerk.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generar un itinerario autenticado (Priority: P1)

Una persona autenticada envía ciudad, fecha, número de personas y gustos, y recibe un itinerario que puede distinguir claramente por mañana, tarde y noche.

**Why this priority**: Generar el itinerario es el valor principal del servicio; la autenticación protege esta operación.

**Independent Test**: Enviar una solicitud válida con un token Clerk válido y una respuesta simulada del proveedor de IA; comprobar el estado, el contrato de respuesta y las tres franjas del itinerario.

**Acceptance Scenarios**:

1. **Given** un token Clerk válido y datos dentro de los límites, **When** la persona solicita un itinerario, **Then** recibe HTTP 200 con `{"resultado": "..."}` y el resultado contiene las líneas `Mañana:`, `Tarde:` y `Noche:` en ese orden.
2. **Given** una solicitud autenticada con datos válidos, **When** los gustos contienen texto que intenta alterar las instrucciones del servicio, **Then** ese texto se trata como dato de entrada y no anula la tarea ni revela instrucciones internas o secretos.

### User Story 2 - Rechazar solicitudes no autenticadas (Priority: P1)

Una persona sin una sesión Clerk válida recibe una respuesta de autenticación clara y no provoca una consulta al proveedor de IA.

**Why this priority**: El backend debe exigir autenticación real; proteger solo la interfaz no impide el acceso directo al servicio.

**Independent Test**: Enviar solicitudes sin token, con token inválido o caducado y con firma de una clave distinta; comprobar HTTP 401, el cuerpo de error y que el proveedor de IA no recibe llamadas.

**Acceptance Scenarios**:

1. **Given** una solicitud sin token, **When** se llama al servicio, **Then** recibe HTTP 401 con `{"error": {"codigo": "NO_AUTENTICADO", "mensaje": "..."}}` y no se consulta la IA.
2. **Given** un token con firma inválida, emisor incorrecto o caducidad vencida, **When** se llama al servicio, **Then** recibe el mismo contrato HTTP 401 y no se consulta la IA.
3. **Given** una solicitud no autenticada cuyos datos también son inválidos, **When** se llama al servicio, **Then** prevalece HTTP 401 sobre la validación de entrada y no se consulta la IA.
4. **Given** un token válido, **When** se valida su autenticidad, **Then** se acepta únicamente si su firma RS256 corresponde a una clave publicada por el JWKS del emisor configurado, el emisor coincide y el token no está caducado; la audiencia solo se comprueba si está configurada.

### User Story 3 - Recibir errores de entrada y del proveedor con un contrato estable (Priority: P2)

Una persona que envía datos incorrectos o cuya solicitud no se puede completar recibe un error identificable y consistente, sin información interna sensible.

**Why this priority**: Un contrato estable permite que quien consume el servicio distinga errores de entrada de problemas temporales o internos.

**Independent Test**: Simular datos inválidos y los distintos fallos del proveedor de IA; verificar estados, códigos y forma común del cuerpo, sin conexiones externas.

**Acceptance Scenarios**:

1. **Given** una solicitud autenticada con ciudad, gustos, personas o fecha fuera de los límites, **When** se envía, **Then** recibe HTTP 422 con el cuerpo de validación de FastAPI (`{"detail": [...]}`), idéntico al de la App 1.
2. **Given** una solicitud autenticada válida y el proveedor de IA no disponible, **When** se solicita el itinerario, **Then** recibe HTTP 502 con código `IA_NO_DISPONIBLE` y el cuerpo común de error.
3. **Given** una solicitud autenticada válida y el proveedor de IA excede el tiempo de espera, **When** se solicita el itinerario, **Then** recibe HTTP 504 con código `IA_TIMEOUT` y el cuerpo común de error.
4. **Given** una solicitud autenticada válida y ocurre un fallo interno inesperado, **When** se solicita el itinerario, **Then** recibe HTTP 500 con código `ERROR_INTERNO` y el cuerpo común de error, sin trazas ni secretos.

### Edge Cases

- Los límites inclusivos son: ciudad de 1 a 80 caracteres, gustos de 1 a 200 caracteres y de 1 a 20 personas.
- La fecha de hoy y las fechas futuras son válidas; una fecha anterior a hoy no lo es.
- La ausencia de una credencial, una credencial malformada, una firma que no corresponde a una clave del JWKS, un emisor no coincidente, una caducidad vencida o una audiencia incorrecta cuando está configurada deben producir 401.
- Una solicitud no autenticada debe producir 401 antes de cualquier error de validación de entrada y antes de cualquier llamada a la IA.
- Una entrada inválida de una persona autenticada debe producir 422 sin llamar a la IA.
- Los errores 401, 502, 504 y 500 deben conservar el objeto superior `error` con las propiedades `codigo` y `mensaje`; el 422 conserva el cuerpo `{"detail": [...]}` de la validación de FastAPI, idéntico al de la App 1.
- Las respuestas de la API deben incluir las mismas cabeceras de seguridad que App 1.
- `/docs`, `/redoc` y `/openapi.json` solo están disponibles cuando `DOCS_ACTIVOS=1`; en Vercel no se define esa variable.
- Las pruebas deben ejecutarse sin internet ni créditos: las llamadas a Clerk/JWKS y al proveedor de IA se sustituyen por dobles locales o mocks.
- La funcionalidad se limita a `app2/backend`; no incluye cambios del frontend.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servicio MUST exponer `POST /api/plan` para solicitar un itinerario con `ciudad`, `gustos`, `personas` y `fecha`.
- **FR-002**: El servicio MUST aceptar ciudad con entre 1 y 80 caracteres, gustos con entre 1 y 200 caracteres y entre 1 y 20 personas.
- **FR-003**: El servicio MUST aceptar una fecha no anterior al día actual y rechazar fechas anteriores con HTTP 422.
- **FR-004**: Para una solicitud válida y autenticada, el servicio MUST responder HTTP 200 con `{"resultado": "..."}`; el texto MUST presentar las secciones `Mañana:`, `Tarde:` y `Noche:` en ese orden.
- **FR-005**: El servicio MUST responder a entradas inválidas con HTTP 422 usando el cuerpo de validación de FastAPI (`{"detail": [...]}`), **idéntico al de la App 1**, sin añadir códigos propios; el resto de errores (`401`, `502`, `504`, `500`) MUST usar `{"error": {"codigo": "...", "mensaje": "..."}}`.
- **FR-006**: El servicio MUST validar el token de sesión Clerk antes de validar los datos de entrada y antes de llamar al proveedor de IA.
- **FR-007**: Si falta el token o este es inválido, está caducado o no supera la verificación de firma, emisor o audiencia aplicable, el servicio MUST responder HTTP 401 con código `NO_AUTENTICADO` y no MUST llamar al proveedor de IA.
- **FR-008**: La autenticación MUST verificar la firma RS256 contra las claves JWKS publicadas en `CLERK_ISSUER + "/.well-known/jwks.json"`, comprobar que `iss` coincide con `CLERK_ISSUER` y que `exp` no ha vencido, y comprobar `aud` únicamente cuando `CLERK_AUDIENCE` esté definida.
- **FR-009**: El servicio MUST traducir indisponibilidad de IA a HTTP 502 y código `IA_NO_DISPONIBLE`, timeout de IA a HTTP 504 y código `IA_TIMEOUT`, y fallos internos inesperados a HTTP 500 y código `ERROR_INTERNO`. Los tres errores MUST usar el formato común `{"error": {"codigo": "...", "mensaje": "..."}}`.
- **FR-010**: Los mensajes de error MUST ser seguros para quien consume el servicio y MUST NOT incluir trazas, tokens, claves ni otros secretos.
- **FR-011**: Las respuestas de la API MUST incluir las cabeceras de seguridad de App 1.
- **FR-012**: El servicio MUST exponer `/docs`, `/redoc` y `/openapi.json` únicamente cuando `DOCS_ACTIVOS=1`; en el despliegue Vercel esta variable no estará definida y dichas rutas no estarán disponibles.
- **FR-013**: `CLERK_SECRET_KEY` MUST permanecer en la configuración privada del backend y MUST NOT exponerse al cliente, al bundle del frontend ni a respuestas de la API. La configuración de Clerk puede referenciar los nombres `CLERK_SECRET_KEY`, `CLERK_ISSUER` y, opcionalmente, `CLERK_AUDIENCE`, sin incluir valores secretos en el repositorio ni en la documentación.
- **FR-014**: El texto de ciudad y gustos MUST tratarse como datos no confiables; instrucciones incluidas en esos campos MUST NOT anular la generación solicitada ni provocar la revelación de instrucciones internas o secretos.
- **FR-015**: La suite MUST cubrir la autenticación, la validación, los errores del proveedor, el formato del itinerario y la inyección de prompt. MUST poder ejecutarse mediante pytest sin internet ni créditos, usando mocks o dobles locales para autenticación, JWKS y generación de itinerarios.
- **FR-016**: La suite MUST comprobar que un token firmado por una clave distinta de la publicada por el JWKS es rechazado con HTTP 401; las pruebas de firma MUST poder realizarse sin depender de un servicio remoto.

### Key Entities *(include if feature involves data)*

- **Solicitud de itinerario**: Ciudad, gustos, número de personas y fecha solicitada, además del token de sesión presentado para autorizar la operación.
- **Token de sesión Clerk**: Credencial cuya firma, emisor, caducidad y audiencia opcional determinan si se autoriza la solicitud.
- **Itinerario**: Texto generado para la solicitud, organizado en las secciones de mañana, tarde y noche.
- **Error de API**: Respuesta con un código estable y un mensaje seguro para quien consume el servicio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las solicitudes autenticadas con entradas válidas de los casos de aceptación reciben HTTP 200 y un resultado con las tres secciones horarias en el orden requerido.
- **SC-002**: El 100 % de las solicitudes sin token o con tokens inválidos, caducados, con firma ajena, emisor incorrecto o audiencia incorrecta cuando aplica reciben HTTP 401, y el contador de llamadas a IA permanece en cero.
- **SC-003**: El 100 % de los casos de límites y errores de entrada reciben HTTP 422 con el cuerpo `detail` idéntico al de la App 1; la fecha de hoy y las fechas futuras se aceptan y una fecha pasada se rechaza.
- **SC-004**: El 100 % de los escenarios simulados de indisponibilidad, timeout y error interno se traducen respectivamente en 502 `IA_NO_DISPONIBLE`, 504 `IA_TIMEOUT` y 500 `ERROR_INTERNO`.
- **SC-005**: La suite completa de backend pasa sin conexiones de red ni consumo de créditos e incluye casos para tokens firmados por una clave distinta y para intentos de inyección de prompt.
- **SC-006**: Quienes consumen el servicio pueden identificar las tres franjas del itinerario sin ambigüedad en todas las respuestas correctas verificadas.

## Assumptions

- El token de sesión se envía en la cabecera `Authorization` como credencial Bearer, de acuerdo con el uso habitual de Clerk.
- `fecha` representa una fecha de calendario ISO (`YYYY-MM-DD`); “hoy” se determina con la fecha de calendario vigente en el backend.
- El contrato de errores es el de la App 1: el `422` de validación conserva el cuerpo `{"detail": [...]}` de FastAPI (la App 1 no define `codigo` en la validación) y los códigos explícitamente fijados para la App 2 son `NO_AUTENTICADO`, `IA_NO_DISPONIBLE`, `IA_TIMEOUT` y `ERROR_INTERNO`, todos dentro de `{"error": {"codigo", "mensaje"}}`.
- La autenticación se verifica con las claves públicas del JWKS del emisor; las pruebas deben sustituir cualquier acceso remoto por claves y respuestas locales simuladas.
- La integración de generación de itinerarios y la lista de cabeceras de seguridad se mantienen compatibles con App 1; el alcance no incluye modificar esa aplicación ni el frontend de App 2.
