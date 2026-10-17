# Despliegues — Vercel, Clerk, Docker y AWS EC2

> URLs y valores concretos se añaden al ejecutarlos. **Sin secretos**: aquí solo configuración
> no secreta, comandos y evidencias.

## 1. URLs (estado de la entrega)

| App | Capa | URL | Fecha | Versión Git | Estado |
|---|---|---|---|---|---|
| App 1 | Vercel (frontend + API) | _(pendiente)_ | | | ⬜ H7 |
| App 2 | Vercel (frontend + API) | _(pendiente)_ | | | ⬜ H10 |
| App 2 | EC2 (Docker, HTTPS) | _(pendiente)_ | | | ⬜ H11 |

## 2. Vercel — un proyecto por aplicación

Un solo proyecto de Vercel por aplicación: sirve los estáticos de Vite **y** la API,
así que front y back comparten origen y **no hace falta CORS** en despliegue.

| Proyecto | Raíz | Publica | Variables |
|---|---|---|---|
| `app1` | `app1/` | estáticos de Vite (`frontend/dist/`) + la API como función Python: `api/plan.py` reexporta el `app` de `backend/main.py` y atiende `/api/plan` (sin rewrite); `maxDuration: 60`; dependencias desde `app1/requirements.txt` | `VITE_API_BASE_URL` **vacía** (mismo origen) + `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT` (**sin** `DOCS_ACTIVOS`: en Vercel `/docs` debe dar 404) |
| `app2` | `app2/` | estáticos de Vite + FastAPI como función Python (mismo esquema) | `VITE_API_BASE_URL` vacía + claves de IA + `VITE_CLERK_PUBLISHABLE_KEY` / `CLERK_SECRET_KEY` |

El `vercel.json` con las **10 cabeceras de seguridad** (S20) vive en la raíz de la
aplicación (`app1/vercel.json`) y se aplica igual a estáticos y a la API.

### 2.1 Procedimiento CLI (reproducible)

```bash
npm install -g vercel && vercel --version
vercel login
vercel link                       # desde la raíz de la aplicación (app1/, app2/, …)
vercel env add AI_API_KEY         # introducir el valor de forma interactiva (nunca en el historial)
vercel deploy
vercel deploy --prod
```

- Distinguir **Development / Preview / Production**; cambiar variables implica volver a desplegar.
- Si en algún momento front y API acaban en dominios distintos, ahí sí hay que abrir CORS
  (`CORS_ORIGINS` en el backend) y comprobar el preflight contra el origen real.

### 2.1b Despliegue de App 1 (un solo proyecto, un solo despliegue)

1. `cd app1 && vercel link` → crea el proyecto (raíz `app1/`) y `vercel --prod`. Anota la URL.
2. Probar la API: `curl -X POST https://xxxx.vercel.app/api/plan -H "Content-Type: application/json" -d "{}"` → tiene que devolver `422`.
3. Probar el flujo completo desde `https://xxxx.vercel.app` (mismo origen: sin CORS).
4. Comprobar las cabeceras con `curl -I https://xxxx.vercel.app` y cerrar **S19**.
5. Anotar URL, fecha y versión Git en la tabla de la sección 1.

Notas:

- `VITE_API_BASE_URL` se deja **vacía** en el panel: el front llama a `/api/plan` en su propio
  origen. Así no hay CORS y no hace falta re-desplegar nada si cambia la URL.
- El `.env` local **no se sube** (`.vercelignore`); las variables se ponen en el panel o con `vercel env add`.
- `main.py`, `ia.py` y `formato.py` no se tocan para desplegar: `load_dotenv()` sin `.env` no hace nada y `--no-server-header` es flag de uvicorn, que en Vercel no se usa.

### 2.2 Comprobación de cierre (App 1 en Vercel)

- [ ] URL pública correcta.
- [ ] Caso válido → `200` con JSON desde la URL desplegada.
- [ ] Caso de error (422 o 502 simulado) visible en la misma pantalla.
- [ ] `curl -I` devuelve las 10 cabeceras del `vercel.json` (S19) y `/docs` da `404`.
- [ ] Ninguna clave en el frontend (buscar en `dist/` y en la pestaña Network).
- [ ] Evidencia de CLI (`vercel ls` / salida del deploy), no solo captura del panel.

## 3. Clerk (solo App 2)

- [ ] Aplicación creada en Clerk; orígenes permitidos: `localhost:5173`, URL Vercel y URL de EC2.
- [ ] Google habilitado como proveedor de acceso.
- [ ] Componente modal/embebido en la **única** pantalla (sin rutas nuevas de login).
- [ ] Frontend envía `Authorization: Bearer <session token>`; backend verifica firma, emisor, caducidad y audiencia.
- [ ] **Evidencia:** petición sin token → `401` (captura) y con sesión válida → `200`.
- [ ] Solo `VITE_CLERK_PUBLISHABLE_KEY` en el frontend; la secreta solo en backend.

## 4. Docker local (solo App 2)

```bash
docker --version && docker compose version
docker compose build
docker compose up -d
docker compose ps
docker compose logs
# probar: entrada válida · error · acceso Clerk · reinicio → sin historial (no hay persistencia)
docker compose down
```

- `infra/Dockerfile.backend` → Python/FastAPI con **uvicorn en `0.0.0.0`** (puerto interno elegido).
- `infra/Dockerfile.frontend` → compila Vite y sirve estáticos; **proxy** reenvía `/api` al backend (URL única de origen).
- **Sin** servicios de BD, volúmenes de datos ni cachés.
- `.dockerignore` excluye `.env`, credenciales y dependencias; los secretos se inyectan **al ejecutar**, nunca en la imagen.
- Las variables `VITE_*` se resuelven en compilación: cambiar la URL exige reconstruir.

## 5. AWS EC2 (solo App 2)

1. [ ] Acceso, región y presupuesto confirmados con el docente; costes revisados antes de crear recursos.
2. [ ] Instancia pequeña; clave SSH protegida; anotar SO, región y tamaño.
3. [ ] Grupo de seguridad: SSH **solo desde IPs autorizadas**; solo puertos web (80/443) publicados.
4. [ ] Docker + Compose instalados; código traído del repositorio **sin credenciales**.
5. [ ] Secretos en el servidor, fuera del repo y con permisos restringidos.
6. [ ] **URL pública con HTTPS** (proxy con TLS + DNS) para probar Clerk con tokens — nunca enviar credenciales por HTTP.
7. [ ] Prueba desde otro dispositivo: frontend, acceso, respuesta IA y errores. Anotar URL, versión Git, puertos y procedimiento de actualización.
8. [ ] Recuperación tras reinicio documentada (política simple de contenedores; sin logs con respuestas).
9. [ ] **Retirada de recursos al finalizar** (instancia, discos, IPs reservadas) según instrucciones del docente.

**Evidencia mínima:** Dockerfile(s), `compose.yaml`, configuración no secreta, instrucciones
reproducibles y captura/registro de la demo funcionando en EC2 (una instancia creada sin app
accesible no vale).

## 6. Problemas de despliegue (añadir cuando ocurran)

| Fecha | Problema | Causa | Solución |
|---|---|---|---|
| | | | |
