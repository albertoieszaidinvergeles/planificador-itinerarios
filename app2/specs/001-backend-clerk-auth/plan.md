# Implementation Plan: Backend autenticado de App 2

**Branch**: `001-backend-clerk-auth` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-backend-clerk-auth/spec.md`

## Summary

Implementar el backend FastAPI dentro de `app2/backend`, manteniendo el endpoint y los límites del contrato de App 1, verificando los session tokens Clerk mediante firma RS256 y JWKS antes de procesar el cuerpo, y normalizando los errores al formato de la spec. Reutilizar el patrón de generación, saneado, formato del plan, CORS y cabeceras de seguridad de App 1 sin modificar `app1/` ni `app2/frontend/`. La configuración de dependencias Python se limita a `app2/backend/requirements.txt`.

## Technical Context

**Language/Version**: Python; usar una versión compatible con las dependencias del backend y el runtime de despliegue existente.

**Primary Dependencies**: FastAPI, Pydantic (incluido por FastAPI), httpx, python-dotenv, `PyJWT[crypto]` para validar firma RS256/JWKS, pytest y las dependencias ya usadas por App 1.

**Storage**: N/A; no hay usuarios propios ni persistencia.

**Testing**: pytest con TestClient, generación IA simulada, claves RSA locales y verificación Clerk/JWKS sustituible por dobles locales; bloquear explícitamente la salida de red en pruebas.

**Target Platform**: Servicio Python local y runtime Python de Vercel ya previsto; no añadir archivos al frontend ni a `app1/`.

**Project Type**: Backend HTTP FastAPI de un solo servicio.

**Performance Goals**: No se especifica un objetivo de latencia; la verificación no debe llamar a OpenRouter para tokens ausentes o inválidos.

**Constraints**: `POST /api/plan` conserva los campos y límites especificados; 401 antes de validar el cuerpo y antes de IA; el `422` se devuelve **igual que en App 1** (`{"detail":[...]}`, sin sobre `error`) y los `401`/`502`/`504`/`500` usan `{"error":{"codigo","mensaje"}}`; ningún secreto en código, documentación o frontend; pruebas sin internet ni créditos; no ejecutar instalaciones.

**Configuration**:
- `CORS_ORIGINS`: lista de orígenes frontend separada por comas; permitir `POST` y los encabezados `Content-Type` y `Authorization` para la sesión Clerk. Permitir preflight `OPTIONS` sin exigir token.
- `DOCS_ACTIVOS=1`: solo entorno local; por defecto y en Vercel debe quedar sin definir/desactivado.
- Cabeceras de seguridad exactamente iguales a App 1: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`, `Strict-Transport-Security: max-age=63072000; includeSubDomains` y, en `/api/`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'`.
- Clerk: `CLERK_SECRET_KEY` privada del backend; `CLERK_ISSUER` para verificar `iss` y obtener el JWKS de `/.well-known/jwks.json`; `CLERK_AUDIENCE` opcional y comprobada solo si tiene valor. La validación de firma RS256 usa las claves públicas JWKS; no debe exponerse ni enviarse la secret key al cliente.
- IA: reutilizar `AI_API_KEY`, `AI_MODEL` y `AI_TIMEOUT` del `.env.example` existente; `CORS_ORIGINS`, `DOCS_ACTIVOS` y las tres variables Clerk ya están documentadas en ese ejemplo. `DOCS_ACTIVOS=1` es un valor de desarrollo local, no de producción.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Aplicación en el diseño |
|---|---|---|
| I. Contrato no negociable | PASS | Mantener ruta y propiedades de entrada/éxito; el `422` conserva el cuerpo `detail` de App 1 y los `401`/`502`/`504`/`500` usan el sobre `error` descrito en la spec. |
| II. Cero secretos | PASS | Leer secretos solo de entorno/`.env` ignorado; ejemplos contienen nombres y placeholders; no se copia configuración secreta al cliente ni a documentos. |
| III. Clerk como identidad única | PASS | Verificar criptográficamente el token de sesión, sin tablas ni usuarios propios; el rechazo ocurre antes de entrada e IA. |
| IV. Pruebas offline y TDD | PASS | Escribir tests antes de la implementación; dobles locales para JWKS, claves y proveedor IA; impedir conexiones externas en pytest. |
| V. Entorno limpio | PASS | Registrar dependencias únicamente en `app2/backend/requirements.txt`; no ejecutar pip ni instalar fuera del `.venv` del backend. |
| VI. Estado y límites | PASS | No añadir persistencia, cachés de aplicación, contadores ni rate limiting; estos límites pertenecen al borde/plataforma. |
| Alcance solicitado | PASS | No editar `app2/frontend/` ni `app1/`; los archivos de código y pruebas nuevos quedan dentro de `app2/backend/`. |

No se identifica una violación que requiera justificación.

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-clerk-auth/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── plan-api.md
```

### Source Code (repository root)

```text
app2/backend/
├── main.py                 # FastAPI app, endpoint, error translation, CORS and security headers
├── auth.py                 # Clerk Bearer/JWKS token verification
├── ia.py                   # OpenRouter request, prompt protections and IA error types
├── formato.py              # Input sanitization and output format validation
├── requirements.txt        # All Python dependencies for this backend and pytest
└── tests/
    ├── conftest.py         # Offline network guard and shared fixtures
    ├── test_auth.py        # Missing, invalid, expired, wrong issuer/audience/signature and valid tokens
    ├── test_plan.py        # Endpoint order, validation, response and error contract
    └── test_formato.py     # Prompt-injection handling and itinerary format
```

**Structure Decision**: Backend-only FastAPI project, organized as the small top-level modules already used by App 1. Keep test modules under `app2/backend/tests/`. Do not add a Vercel adapter, frontend changes, or files to App 1 as part of this backend-only plan. Deployment routing is an external integration concern; this plan exposes the ASGI `app` from the backend entry point but does not claim to provision or change Vercel routing.

## Phase 0: Research

See [research.md](research.md). Decisions are based on the feature spec, the App 2 constitution, the existing App 2 `.env.example`, and read-only inspection of App 1's backend patterns. No internet access is needed for implementation or tests.

## Phase 1: Design & Contracts

- [Data model](data-model.md): request, session token, itinerary response, and API error values.
- [API contract](contracts/plan-api.md): request/response shapes, auth precedence, status codes, CORS and docs configuration.
- [Quickstart](quickstart.md): local setup and offline verification procedure.

## Constitution Check (post-design)

| Gate | Result |
|---|---|
| Public response contract and route retained | PASS |
| Authentication verifies signature, issuer, expiration, and optional audience before body validation/AI | PASS |
| No user storage, secret exposure, frontend or App 1 edits | PASS |
| Tests can run fully offline with mocked Clerk/JWKS and IA | PASS |
| Python dependency changes are limited to `app2/backend/requirements.txt`; no installation performed | PASS |
| Local docs only; production docs disabled; CORS and security headers specified | PASS |

No constitution violations remain.

## Complexity Tracking

No added complexity or constitution exceptions.
