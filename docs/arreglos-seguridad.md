# Arreglos de seguridad — cómo aplicarlos uno a uno

> **Fecha:** 15/10/2026 · **Origen:** resultados de `docs/pruebas.md` (§ «Pruebas de seguridad (App 1)», S01–S20).
> **Regla que no se rompe:** ninguno de estos cambios toca el contrato `POST /api/plan`
> (`200 {"resultado": ...}` / errores `{"error": {"codigo", "mensaje"}}`) ni el archivo `ia.py`.

## Estado en un vistazo

| # | Arreglar | Dónde | Quién | Estado |
|---|---|---|---|---|
| 1 | Límite de tamaño del cuerpo (`413`) | `app1/backend/main.py` | Manuel | 💬 Propuesta: riesgo aceptado, sin código (ver nota) — pendiente de acordar en equipo |
| 2 | Rate limit en el borde (`429`) + alerta de gasto | SE ARREGLA EN VERCEL | Equipo | ⏳ Pendiente |
| 3 | Desactivar `/docs`, `/redoc`, `/openapi.json` en producción | `app1/backend/main.py` | Manuel | ✅ Hecho 16/10/2026 (`DOCS_ACTIVOS`) |
| 4 | Cabeceras de seguridad del backend + ocultar `server: uvicorn` | `app1/backend/main.py` + arranque de uvicorn | Manuel | ✅ Hecho 16/10/2026 (con cambios respecto a esta guía, ver nota) |

### Nota de implementación (16/10/2026, Manuel)

- **Punto 4 — el código de la guía no se puede usar tal cual:**
  - `respuesta.headers.pop("server", None)` **falla**: las cabeceras de Starlette (`MutableHeaders`, Starlette 1.8.0)
    no tienen método `pop`. Con ese código, **todas** las peticiones habrían acabado en `500`.
  - Además la cabecera `server: uvicorn` no la añade FastAPI sino uvicorn **al enviar** la respuesta, así que el
    middleware no puede verla. Se quita arrancando con `uvicorn main:app --reload --no-server-header`.
  - La CSP `default-src 'none'` se aplica **solo a `/api/`**: en `/docs` dejaba Swagger en blanco (bloquea su JavaScript).
  - `Strict-Transport-Security` se envía siempre: el navegador la ignora si llega por `http` (local).
  - Verificado: 19 tests en verde (test nuevo de cabeceras), cabeceras visibles en la pestaña Network, CORS intacto
    y sin `server: uvicorn`.
- **Punto 3:** `/docs`, `/redoc` y `/openapi.json` solo existen con `DOCS_ACTIVOS=1` (en el `.env` local y en
  `.env.example`); sin la variable → `404`. Verificado en local en los dos estados.
- **Punto 1 — propuesta de no implementarlo:** en producción Vercel ya rechaza cuerpos de más de 4,5 MB; y un cuerpo
  grande que llegue lo rechaza Pydantic con `422` **antes** de llamar a la IA (no gasta cuota). Un `413` propio añadiría
  un código que no está en el contrato de la ERS. Se propone documentarlo como riesgo aceptado; pendiente de decidir
  entre los dos.

---

## 1. Límite de tamaño del cuerpo → `413`

**Qué falló (S13):** se envió un JSON de **4,8 MB** y el backend lo aceptó y procesó
(solo lo rechazó la validación de campos, y solo porque el texto no cabía en `gustos`).
**Por qué importa:** un puñado de peticiones grandes puede llenar la memoria y tumbar el
proceso; y si el cuerpo pasara la validación, cada uno costaría una llamada de pago a OpenRouter.

**Cómo se arregla** — en `app1/backend/main.py`, *debajo* de la función `respuesta_error`
(el middleware la necesita definida) y después del CORS:

```python
# --- Límite de tamaño del cuerpo (prueba S13) ---
# Un plan real pesa ~1 KB; 64 KB es un margen enorme y legítimo.
MAX_CUERPO = 64 * 1024


@app.middleware("http")
async def limite_de_tamano(request: Request, call_next):
    """Rechaza antes de leer el cuerpo si Content-Length supera MAX_CUERPO."""
    tamano = request.headers.get("content-length")
    if tamano is not None and tamano.isdigit() and int(tamano) > MAX_CUERPO:
        return respuesta_error(
            413, "CUERPO_DEMASIADO_GRANDE", "El cuerpo de la petición es demasiado grande."
        )
    return await call_next(request)
```

Notas:

- El error **usa el mismo sobre del contrato** `{"error": {"codigo", "mensaje"}}`; el camino
  válido sigue siendo `200 {"resultado": ...}` y los `422` de validación no cambian.
- Si la petición viene sin `Content-Length` (chunked), el `if` no hace nada: es el caso raro,
  lo cubre el límite del propio runtime en Vercel.
- Alternativa sin tocar Python: `client_max_body_size` en el proxy/Nginx delante del backend.

**Cómo se verifica:**

```bash
# grande (debe dar 413)
python -c "open('grande.json','w').write('{\"ciudad\":\"'+'a'*5000000+'\"}')"
curl -i -X POST -H "Content-Type: application/json" --data-binary @grande.json http://127.0.0.1:8000/api/plan

# válido (debe seguir dando 200)
curl -i -X POST -H "Content-Type: application/json" \
  -d '{"ciudad":"Sevilla","fecha":"2027-01-01","personas":2,"gustos":"museos y tapas"}' \
  http://127.0.0.1:8000/api/plan
```

---

## 2. Rate limit en el borde (`429`) + alerta de gasto

**Qué falló (S12):** 100 peticiones seguidas sin un solo `429`; **cada petición válida cuesta
una llamada a OpenRouter** (el sqlmap provocó 73 intentos en ~1 minuto).
**Por qué no se pone dentro de la app:** el enunciado prohíbe cachés y contadores en memoria,
así que la limitación va **delante** del backend (proxy/CDN) o en la factura del proveedor.

**Cómo se arregla (elegir una vía, o las dos):**

 
NO ARREGLAR SE HACE EN VERCEL

## 3. Cerrar `/docs`, `/redoc` y `/openapi.json` en producción

**Qué falló (S08):** con `ffuf` (4.700 rutas) la **única** ruta `200` fue `/docs`; además
`/openapi.json` y `/redoc` responden. Explican el contrato completo a cualquiera.
**Por qué importa:** reduce la superficie y evita que copien la firma exacta de la API.

**Cómo se arregla** — en `app1/backend/main.py`, sustituyendo la línea 24
(`app = FastAPI(title="Planificador de itinerarios")`):

```python
# Los docs solo se abren si DOCS_ACTIVOS=1 (en local va en el .env; en Vercel no se define).
DOCS_ACTIVOS = os.getenv("DOCS_ACTIVOS", "0") == "1"

app = FastAPI(
    title="Planificador de itinerarios",
    docs_url="/docs" if DOCS_ACTIVOS else None,
    redoc_url="/redoc" if DOCS_ACTIVOS else None,
    openapi_url="/openapi.json" if DOCS_ACTIVOS else None,
)
```

- En **local**: añadir `DOCS_ACTIVOS=1` a `app1/backend/.env` para seguir usando el Swagger.
- En **Vercel**: no se define la variable → todo `404`.
- **No toca el contrato:** `/api/plan` es independiente de la documentación.

**Cómo se verifica:**

```bash
curl -i https://<backend>/docs          # 404
curl -i https://<backend>/openapi.json  # 404
# y el endpoint sigue vivo:
curl -i -X POST -H "Content-Type: application/json" \
  -d '{"ciudad":"Sevilla","fecha":"2027-01-01","personas":2,"gustos":"tapas"}' \
  https://<backend>/api/plan
```

---

## 4. Cabeceras de seguridad del backend + ocultar `server: uvicorn`

**Qué falló (S14/S15):** faltan `Content-Security-Policy`, `Strict-Transport-Security`,
`X-Content-Type-Options`, `Referrer-Policy` y `Permissions-Policy`; y la respuesta se firma
con `server: uvicorn` (informa de la pila exacta a un atacante).

**Cómo se arregla** — en `app1/backend/main.py`, al final (después del endpoint):

```python
# --- Cabeceras de seguridad (prueba S14) ---
CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    # La API solo devuelve JSON y no incrusta nada: 'none' es suficiente.
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
}


@app.middleware("http")
async def cabeceras_de_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    for clave, valor in CABECERAS_SEGURIDAD.items():
        # setdefault: no pisa las cabeceras que ya pone CORS.
        respuesta.headers.setdefault(clave, valor)
    # HSTS solo tiene sentido tras TLS (en local con http no se envía).
    if request.url.scheme == "https":
        respuesta.headers.setdefault(
            "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
        )
    # Oculta la firma del servidor aunque vaya por otro camino.
    respuesta.headers.pop("server", None)
    return respuesta
```

Y en el **arranque** de uvicorn, para no enviar el `Server` por defecto:

```bash
py -3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-server-header
```

(En Vercel la cabecera `server` la controla la plataforma; ahí no hace falta el flag.)

**Advertencia de orden:** este middleware debe ir *después* del `CORSMiddleware` y usar
`setdefault`, para que no tape el `access-control-allow-origin` que necesita el frontend.

**Cómo se verifica:**

```bash
curl -i -X OPTIONS https://<backend>/api/plan -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST"
```

Esperado: aparecen todas las cabeceras nuevas **y sigue apareciendo**
`access-control-allow-origin: http://localhost:5173`.

---


## Checklist final de verificación

- [ ] `413` con cuerpo de 4,8 MB y `200` con el cuerpo normal (punto 1)
- [ ] `429` aparece en la tanda de 100 peticiones y llega la alerta de OpenRouter (punto 2)
- [ ] `/docs`, `/redoc` y `/openapi.json` → `404` en producción; `/api/plan` sigue en pie (punto 3)
- [ ] Cabeceras nuevas visibles **sin** perder el CORS del frontend (punto 4)
- [ ] `curl -I` al frontend de Vercel devuelve las 10 cabeceras de `vercel.json` (S19)
- [ ] Suite `pytest` en verde antes y después de cada cambio
