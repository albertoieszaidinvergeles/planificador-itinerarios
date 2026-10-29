# Quickstart: Backend autenticado App 2

Guía de implementación y validación local; no instala ni modifica dependencias.

## Prerrequisitos

- Windows y Python disponible en la versión admitida por el runtime.
- Entorno virtual ya existente en `app2/backend/.venv`.
- Dependencias instaladas por el propietario del entorno desde `app2/backend/requirements.txt` (ejecución) y `app2/backend/requirements-dev.txt` (pytest).
- `.env` local del backend copiado desde `.env.example` y configurado sin subirlo a Git. Usar placeholders en documentación y nunca compartir valores reales.

## Configuración local

Desde `app2/backend`:

1. Configurar `CORS_ORIGINS` con el origen exacto del frontend local (por ejemplo, `http://localhost:5173`); admite varios orígenes separados por comas.
2. Definir `DOCS_ACTIVOS=1` solo para desarrollo local.
3. Definir `CLERK_SECRET_KEY` como secreto privado del backend, `CLERK_ISSUER` como issuer de la instancia y opcionalmente `CLERK_AUDIENCE`. Ninguno de esos valores debe ponerse en el frontend ni en commits.
4. Configurar `AI_API_KEY`, `AI_MODEL` y `AI_TIMEOUT` para una ejecución manual con el proveedor. Las pruebas no los necesitan porque la IA está simulada.

## Ejecutar las pruebas (sin red ni créditos)

Activar `.venv` del backend y ejecutar:

```powershell
python -m pytest
```

La suite debe fallar ante cualquier intento de salida de red. Los tests de auth deben usar tokens y claves RSA generados localmente y JWKS simulado; los tests de itinerarios deben sustituir la llamada a IA.

### Verificaciones mínimas

1. Sin cabecera `Authorization`, enviar JSON válido e inválido: ambos deben devolver 401 `NO_AUTENTICADO`, con cero llamadas a la IA.
2. Firmar un token con clave privada local y publicar solo la clave pública de prueba en el JWKS simulado: el token válido devuelve 200; un token firmado por otra clave devuelve 401.
3. Comprobar emisor, expiración y audiencia (audience se omite solo cuando `CLERK_AUDIENCE` no tiene valor).
4. Probar los límites de ciudad (1/80/81), gustos (1/200/201), personas (1/20/0/21) y fecha de ayer/hoy/futuro; errores 422 usan el cuerpo `detail` de FastAPI (igual que App 1) y no llaman a IA.
5. Simular respuestas 502, timeout 504, excepción inesperada 500, salida válida con las tres etiquetas en orden e intentos de inyección de prompt.
6. Comprobar cabeceras de seguridad en respuestas 200, 401, 422 y errores del proveedor; comprobar CORS preflight y que `Authorization` está permitido.
7. Con `DOCS_ACTIVOS` ausente, `/docs`, `/redoc` y `/openapi.json` no están disponibles; con `DOCS_ACTIVOS=1` en local, sí.

La llamada de desarrollo a OpenRouter se valida manualmente y queda fuera de pytest; nunca se requiere acceso real a Clerk/JWKS ni OpenRouter en CI o en la suite.
