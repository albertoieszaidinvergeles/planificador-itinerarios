# Tasks: Backend autenticado de App 2

**Input**: Design documents from `specs/001-backend-clerk-auth/`

**Alcance**: Solo `app2/backend`. No crear tareas para `app2/frontend/` ni `app1/`.

**Pruebas**: TDD obligatorio según la constitución IV. Escribir cada test antes del código que cubre y confirmar que falla antes de implementar. El propietario instala `requirements.txt` y `requirements-dev.txt` en `app2/backend/.venv`; este plan no ejecuta instalaciones.

**Formato**: Todas las tareas incluyen checkbox, ID secuencial, etiqueta `[BACKEND]`, etiqueta de historia cuando corresponde y rutas concretas.

## Phase 1: Setup

**Purpose**: Preparar únicamente el entorno Python y las dependencias declaradas del backend.

- [x] T001 [BACKEND] Crear `app2/backend/.venv` con `python -m venv .venv` si aún no existe; no instalar paquetes en este paso.
- [x] T002 [BACKEND] Crear `app2/backend/requirements.txt` con las dependencias de ejecución (FastAPI, httpx, python-dotenv y `PyJWT[crypto]`) y `app2/backend/requirements-dev.txt` únicamente con `pytest`, igual que en la App 1 para que la producción no instale paquetes de test; no ejecutar pip.

**Gate**: El entorno local está preparado y el propietario puede instalar `requirements.txt` (ejecución) y `requirements-dev.txt` (pytest) dentro de `.venv` antes de ejecutar pytest.

---

## Phase 2: User Story 2 - Rechazar solicitudes no autenticadas (Priority: P1)

**Goal**: Verificar criptográficamente el token Clerk y denegar credenciales inválidas antes de que la solicitud llegue a la IA.

**Independent Test**: Con claves RSA y JWKS simulados localmente, comprobar token válido y rechazo de ausencia, firma ajena, `kid` desconocido, emisor incorrecto, caducidad vencida o ausente, y audiencia incorrecta cuando está configurada. No debe producirse tráfico de red.

### Tests for User Story 2

> Escribir primero y comprobar el fallo antes de implementar `auth.py`.

- [x] T003 [BACKEND] [US2] Preparar `app2/backend/tests/conftest.py` con bloqueo de red para la suite y escribir `app2/backend/tests/test_auth.py` para comprobar firma RS256 con JWKS en memoria, token sin/caducado/con firma de otra clave, `kid` desconocido, `iss` incorrecto y `aud` correcto/incorrecto/opcional; ejecutar el test con `.venv` y confirmar los fallos esperados sin conexión de red.

### Implementation for User Story 2

- [x] T004 [BACKEND] [US2] Implementar `app2/backend/auth.py` para extraer Bearer, validar RS256 solo contra el JWKS derivado de `CLERK_ISSUER`, exigir y verificar `iss` y `exp`, comprobar `aud` solo si `CLERK_AUDIENCE` está definida y traducir credenciales inválidas a un resultado de no autenticación sin exponer errores internos.

**Checkpoint**: Los tests de autenticación de `test_auth.py` pasan usando solo claves y JWKS locales simulados.

---

## Phase 3: User Story 1 - Generar un itinerario autenticado (Priority: P1)

**Goal**: Una solicitud autorizada y válida devuelve el objeto de resultado con el itinerario de un día.

**Independent Test**: Sustituir la IA por un mock y comprobar que una solicitud válida con token aceptado recibe HTTP 200, `{"resultado": "..."}` y las secciones `Mañana:`, `Tarde:` y `Noche:` en ese orden.

### Tests for User Story 1

> Escribir el test del endpoint antes de crear la ruta en `main.py`.

- [x] T005 [BACKEND] [US1] Escribir en `app2/backend/tests/test_plan.py` el caso autenticado válido con HTTP 200, forma exacta `{"resultado": "..."}` y las tres franjas en orden, simulando Clerk e IA; comprobar además que falta de token prevalece sobre un cuerpo inválido con 401 y cero llamadas a IA, y que entrada autenticada inválida devuelve 422 `{"detail":[...]}` idéntico a App 1 sin llamada a IA. Cubrir ciudad 1-80, gustos 1-200, personas 1-20 y fecha hoy/futura frente a fecha pasada.

### Implementation for User Story 1

- [x] T006 [BACKEND] [US1] Implementar en `app2/backend/main.py` la aplicación FastAPI y `POST /api/plan`, conectar la validación Clerk antes del procesamiento del cuerpo, validar ciudad 1-80, gustos 1-200, personas 1-20 y fecha no anterior a hoy, y delegar la generación de forma sustituible por mocks; mantener 200 con `{"resultado": texto}` y 422 idéntico al cuerpo estándar `{"detail":[...]}` de App 1.

**Checkpoint**: El flujo feliz autenticado pasa con la IA simulada y no altera los campos ni la respuesta de éxito del contrato.

---

## Phase 4: User Story 3 - Mantener errores y configuración compatibles (Priority: P2)

**Goal**: Mantener los límites de App 1 y traducir fallos a los estados y cuerpos establecidos, junto con CORS, cabeceras y documentación condicional.

**Independent Test**: Con autenticación e IA simuladas, verificar cuerpos 422 de FastAPI idénticos al contrato App 1; comprobar 502, 504 y 500 con `error.codigo/mensaje`, cero llamadas a IA para entrada inválida, cabeceras de seguridad, CORS/preflight y documentación deshabilitada por defecto.

### Tests for User Story 3

> Escribir estos casos antes de completar el manejo de errores y configuración en `main.py`.

- [x] T007 [BACKEND] [US3] Añadir a `app2/backend/tests/test_plan.py` simulaciones de indisponibilidad, timeout y error inesperado que comprueben respectivamente 502 `IA_NO_DISPONIBLE`, 504 `IA_TIMEOUT` y 500 `ERROR_INTERNO`; comprobar también cabeceras App 1 en respuestas correctas y de error, CORS desde `CORS_ORIGINS` con `POST`, `Content-Type`, `Authorization` y preflight `OPTIONS`, y `/docs`, `/redoc` y `/openapi.json` deshabilitadas sin `DOCS_ACTIVOS=1` y habilitadas cuando vale `1` localmente.

### Implementation for User Story 3

- [x] T008 [BACKEND] [US3] Completar `app2/backend/main.py` con las respuestas 502 `IA_NO_DISPONIBLE`, 504 `IA_TIMEOUT` y 500 `ERROR_INTERNO` en el sobre `error`; configurar CORS desde `CORS_ORIGINS`, permitir preflight `OPTIONS` y encabezados `Content-Type`/`Authorization`, replicar las cabeceras de seguridad de App 1 y exponer `/docs`, `/redoc` y `/openapi.json` solo si `DOCS_ACTIVOS=1`.

**Checkpoint**: `test_plan.py` verifica el contrato completo, la precedencia de 401 sobre la validación y la ausencia de llamadas IA en 401/422.

---

## Phase 5: User Story 1 - Formato e inyección de prompt (Priority: P1)

**Goal**: Tratar los datos del usuario como no confiables y asegurar que la salida de IA conserva el formato que necesita el consumidor.

**Independent Test**: Con la IA simulada, probar datos con saltos de línea y etiquetas de franja, respuestas válidas e inválidas, y errores de IA; el servicio devuelve solo un plan plano válido o el error de proveedor contratado.

### Tests for User Story 1

> Escribir y ejecutar los tests primero; `ia.py` y `formato.py` se implementan después.

- [x] T009 [BACKEND] [US1] Crear `app2/backend/tests/test_formato.py` para probar saneado de ciudad/gustos contra saltos de línea e intentos de inyección, aceptación de las tres etiquetas en orden y rechazo de etiquetas ausentes/repetidas/desordenadas o salida marcada; comprobar mediante mock que la solicitud IA no revela secretos y que la salida inválida se traduce a 502.

### Implementation for User Story 1

- [x] T010 [BACKEND] [US1] Implementar `app2/backend/formato.py` y `app2/backend/ia.py`: sanear datos antes de interpolarlos en el prompt, fijar instrucciones de formato de tres franjas en texto plano, realizar la llamada al proveedor con configuración de entorno, validar la salida, y clasificar indisponibilidad, timeout o respuesta inutilizable sin filtrar secretos.

**Checkpoint**: `test_formato.py` pasa con mocks; pytest no accede a OpenRouter ni consume créditos.

---

## Phase 6: Verificación final

**Purpose**: Ejecutar la suite completa en el entorno acordado y dejar constancia del resultado.

- [x] T011 [BACKEND] Desde `app2/backend`, ejecutar `.venv\Scripts\python.exe -m pytest`, confirmar que la suite completa pasa sin internet ni créditos y anotar comando, resultado y fecha en `docs/pruebas.md`, conforme a la constitución; no instalar paquetes ni modificar `app2/frontend/` o `app1/`.

---

## Dependencies & Execution Order

### Secuencia obligatoria

```text
T001 → T002 → instalación manual por el propietario de requirements.txt y requirements-dev.txt en .venv
     → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011
```

- **Setup**: T001 y T002 preceden a cualquier test; no hay instalación durante la ejecución de estas tareas.
- **US2 (auth)**: T003 establece el bloqueo de red y escribe los tests TDD; T004 implementa `auth.py`.
- **US1 (endpoint)**: T005 escribe el flujo feliz y la precedencia de autenticación antes de T006.
- **US3 (contrato y configuración)**: T007 escribe los casos de error y configuración antes de T008.
- **US1 (prompt y formato)**: T009 es el test previo a T010.
- **Verificación final**: T011 depende de todas las implementaciones y tests anteriores.

### Oportunidades de paralelismo

- No hay tareas de implementación marcadas `[P]`: la secuencia TDD solicitada y los cambios sucesivos en `main.py` requieren orden.
- Una vez completado T002, la instalación de requisitos es una acción manual del propietario; es un prerrequisito de ejecución para T003, no una tarea de instalación del agente.
- Tras completar todos los tests, su ejecución local se agrupa en T011; no se recomienda paralelizar tests contra los mismos módulos en edición.

## Implementation Strategy

1. **MVP autenticado**: preparar entorno y requisitos; escribir `test_auth.py`, implementar y verificar autenticación Clerk; después escribir los tests del endpoint e implementar `main.py`.
2. **Completar contrato**: cubrir primero los casos de validación, errores, CORS, cabeceras y documentación; completar las rutas y traducciones correspondientes en `main.py`.
3. **Proteger generación**: escribir `test_formato.py` antes de implementar saneado, prompt y validación de la salida IA.
4. **Cerrar entrega**: ejecutar pytest en el `.venv` local, sin red ni créditos, y registrar resultado según la constitución.

**MVP sugerido**: fases 1-3 (T001-T006), con pruebas de autenticación y flujo feliz funcionando con la IA simulada. El endpoint no debe considerarse desplegable hasta completar US3, formato/inyección y verificación final.
