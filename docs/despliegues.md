# Despliegues — Vercel, Clerk, Docker y AWS EC2

> URLs y valores concretos se añaden al ejecutarlos. **Sin secretos**: aquí solo configuración
> no secreta, comandos y evidencias.

## 1. URLs (estado de la entrega)

| App | Capa | URL | Fecha | Versión Git | Estado |
|---|---|---|---|---|---|
| App 1 | Vercel (frontend + API) | <https://planificador-itinerarios-iota.vercel.app/> | 19/10/2026 | `984187f` | ✅ H7 **desplegado y verificado (S19)**: `/` → `200` con las 10 cabeceras, `/docs` → `404`, `POST /api/plan` válido → `200 {"resultado": …}` en 5,4 s |
| App 2 | Vercel (frontend + API + proxy Clerk) | <https://planificador-itinerarios.vercel.app/> | 03/11/2026 | — | ✅ H10 desplegado; `/` → `200`, `POST /api/plan` sin sesión → `401`; Alberto confirma una petición real autenticada correcta |
| App 2 | EC2 (Docker, HTTPS) | <https://107-20-112-76.sslip.io/> | 04/11/2026 | `85dc002` | ✅ H11 desplegado y probado: HTTPS con Let's Encrypt, acceso con Google y plan en navegador y móvil, recuperación tras reinicio. **Solo responde mientras el Learner Lab esté iniciado** (ver §5.2) |

> **Nota (19/10/2026):** la URL del *deployment* concreto
> (<https://planificador-itinerarios-6o6a7zvgf-ies-zaidin-vergeles2.vercel.app/>) responde
> `302 Protected by Vercel Authentication` en todas las rutas porque Vercel protege por defecto
> esas URL provisionales (el `6o6a7zvgf` es el ID del despliegue). **La pública es la de la
> tabla:** <https://planificador-itinerarios-iota.vercel.app/> — ahí se ejecutó la **S19**
> completa (`docs/pruebas.md`): 10/10 cabeceras en web **y** en la API, `/docs` → `404`,
> origen malicioso → `400` sin `access-control-allow-origin`, `POST {}` → `422` y `POST`
> válido → `200 {"resultado": …}` en 5,4 s, con `Server: Vercel`.

> **App 2 (03/11/2026):** la URL pública <https://planificador-itinerarios.vercel.app/>
> devuelve `200`. Una petición a `/api/plan` sin sesión devuelve `401`, como exige Clerk;
> Alberto confirma que una petición real con sesión válida sí funciona. No se guardan tokens
> ni datos personales de la prueba. La revisión local de esta documentación no dispone de
> la sesión Clerk para repetir esa petición autenticada.

## 2. Vercel — un proyecto por aplicación

Un solo proyecto de Vercel por aplicación: sirve los estáticos de Vite **y** la API,
así que front y back comparten origen y **no hace falta CORS** en despliegue. La API no queda
ejecutándose como un servidor permanente: Vercel invoca la función Python al llegar una
petición HTTP y puede iniciarla de nuevo cuando sea necesario.

| Proyecto | Raíz | Publica | Variables |
|---|---|---|---|
| `app1` | `app1/` | estáticos de Vite (`frontend/dist/`) + la API como función Python: `api/plan.py` reexporta el `app` de `backend/main.py` y atiende `/api/plan` (sin rewrite); `maxDuration: 60`; dependencias desde `app1/requirements.txt` | `VITE_API_BASE_URL` **vacía** (mismo origen) + `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT` (**sin** `DOCS_ACTIVOS`: en Vercel `/docs` debe dar 404) |
| `app2` | `app2/` | Build `cd frontend && npm install && npm run build`, estáticos en `frontend/dist`; `api/plan.py` exporta `main.app` como función ASGI Python para `/api/plan`; `proxy.js` es Routing Middleware solo para `/__clerk/:path*` | `VITE_API_BASE_URL` vacía, `VITE_CLERK_PUBLISHABLE_KEY` pública y variables servidor `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT`, `CLERK_ISSUER`, `CLERK_AUDIENCE` opcional y `CLERK_SECRET_KEY` para el proxy |

En App 2, `vercel.json` dirige las rutas de la SPA a `index.html` **sin capturar `/api/`**,
para que la petición llegue a `api/plan.py`. Vercel reconoce la exportación ASGI `app`;
no se arranca `uvicorn` ni hace falta un proceso backend aparte. Las llamadas del SDK de
Clerk pasan por `/__clerk`, donde el Routing Middleware reenvía las peticiones a Clerk y
usa `CLERK_SECRET_KEY` solo en el servidor.

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

- [x] URL pública correcta: <https://planificador-itinerarios-iota.vercel.app/> → `200` (19/10/2026).
- [x] Caso válido → `200` con JSON desde la URL desplegada (`POST /api/plan`, 5,4 s, `{"resultado": "Mañana: Visita al Museo…"}`).
- [ ] Caso de error (422 o 502 simulado) visible en la misma pantalla (verificado en local: I02–I03; falta la captura en producción).
- [x] `curl -I` devuelve las 10 cabeceras del `vercel.json` (S19) y `/docs` da `404` — **también en `/api/plan` (10/10)**.
- [x] Ninguna clave en el frontend: el JS servido (`/assets/index-Lwb4RWKW.js`) no contiene `sk-or-`, `AI_API_KEY`, `AI_MODEL` ni `Bearer`.
- [ ] Evidencia de CLI (`vercel ls` / salida del deploy), no solo captura del panel → **falta la tuya**.

### 2.3 App 2 en producción (H10)

- URL pública: <https://planificador-itinerarios.vercel.app/>.
- Verificación directa del 03/11/2026: `GET /` → `200`; `POST /api/plan` sin
  `Authorization` → `401`.
- Manuel confirmó que la petición real con sesión Clerk válida funciona. La prueba
  autenticada requiere la sesión del usuario y no se reproduce con una petición anónima.
- El despliegue no se marca como verificado mediante una petición autenticada independiente
  ni se atribuye a un SHA concreto de Vercel; no se dispone de esa evidencia en esta revisión.

## 3. Clerk (solo App 2)

- [ ] Aplicación creada en Clerk; orígenes permitidos: `localhost:5173`, URL Vercel y URL de EC2.
- [ ] Google habilitado como proveedor de acceso.
- [ ] Componente modal/embebido en la **única** pantalla (sin rutas nuevas de login).
- [ ] Frontend envía `Authorization: Bearer <session token>`; backend verifica firma, emisor, caducidad y audiencia.
- [ ] **Evidencia:** petición sin token → `401` (captura) y con sesión válida → `200`.
- [ ] Solo `VITE_CLERK_PUBLISHABLE_KEY` en el frontend; la secreta solo en backend.

## 4. Docker local (solo App 2)

Dos contenedores: `web` (Caddy: sirve la página compilada, reenvía `/api/*` a `backend` y gestiona
el HTTPS) y `backend` (FastAPI, sin puertos publicados). Front y API comparten dirección: sin CORS.

```powershell
# Desde infra/ (Docker Desktop abierto). La primera vez, copiar y rellenar el .env:
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
docker compose logs --tail 30
# Probar en http://localhost: entrada válida · error · acceso Clerk · recargar → sin historial
docker compose down
```

- `infra/Dockerfile.backend` → Python 3.12 con **uvicorn en `0.0.0.0:8000`**, usuario sin privilegios, sin tests ni secretos.
- `infra/Dockerfile.frontend` → dos fases: Node compila Vite y la imagen final solo lleva Caddy y `dist/`.
- `infra/proxy/Caddyfile` → `{$DOMINIO}`: con `http://localhost` sirve por HTTP; con un dominio público saca y renueva el certificado.
- `infra/compose.yaml` → `restart: unless-stopped`. La clave de la IA solo llega al contenedor `backend`.
- **Sin** servicios de BD, datos de la aplicación ni cachés. Los volúmenes `caddy_data` y `caddy_config` solo guardan los **certificados HTTPS** y la configuración de Caddy (infraestructura, no datos de usuario).
- `.dockerignore` (en la raíz) es una **lista de permitidos**: se ignora todo salvo el código necesario; `.env`, `.venv`, `node_modules` y `.git` no entran. Los secretos se inyectan **al ejecutar**, nunca en la imagen.
- Las variables `VITE_*` se resuelven en compilación: cambiar la publishable key exige reconstruir (`--build`).

## 5. AWS EC2 (solo App 2)

### 5.1 Estado de la lista de comprobación

1. [x] Acceso: **AWS Academy Learner Lab** (cuenta de estudiante con créditos, sin tarjeta). Región `us-east-1`.
2. [x] Instancia `t3.small` (2 vCPU, 2 GiB; compilar el frontend no cabe bien en 1 GiB), Ubuntu Server 24.04 LTS, disco `gp3` de 16 GiB. Clave SSH `vockey` (`labsuser.pem`), guardada fuera del repositorio.
3. [x] Grupo de seguridad: **SSH (22) solo desde «Mi IP»**; HTTP (80) y HTTPS (443) abiertos. El puerto 8000 del backend no se publica (comprobado desde fuera).
4. [x] Docker y Compose instalados desde los paquetes de Ubuntu; código traído del repositorio público **sin credenciales**.
5. [x] Secretos en `infra/.env` del servidor (copiado con `scp`, `chmod 600`), fuera del repositorio y de las imágenes.
6. [x] **URL pública con HTTPS**: <https://107-20-112-76.sslip.io/>, certificado de Let's Encrypt obtenido por Caddy. HTTP redirige a HTTPS (`308`).
7. [x] Prueba desde otro dispositivo (móvil con datos móviles): frontend, acceso y respuesta de la IA. Resultados en `docs/pruebas.md`.
8. [x] Recuperación tras reinicio comprobada: tras `sudo reboot`, la web y la API vuelven solas y se conserva el certificado.
9. [ ] **Retirada de recursos al finalizar** (instancia, disco e IP elástica) según instrucciones del docente.

**Evidencia:** `infra/` (Dockerfiles, `compose.yaml`, `Caddyfile`, `.env.example`), `.dockerignore` y capturas en
`docs/evidencias/ec2/`: [candado HTTPS](evidencias/ec2/01-https-candado.png),
[plan en tarjetas](evidencias/ec2/02-plan-en-tarjetas.png) y [`docker compose ps`](evidencias/ec2/03-docker-compose-ps.png).

### 5.2 Learner Lab: lo que hay que saber antes de la demo

- **La máquina solo funciona con el laboratorio iniciado.** Al acabar la sesión (o con **End Lab**) se apaga, sin borrarse. Antes de la defensa: AWS Academy → **Start Lab** → esperar el círculo verde → comprobar la URL.
- Al encender, Docker arranca solo y `restart: unless-stopped` levanta los contenedores: no hay que ejecutar nada.
- La **IP elástica** mantiene la dirección y, por tanto, el dominio y el certificado.
- **Conectarse por SSH desde otra red:** la regla SSH solo admite la IP con la que se creó. Con otra wifi la conexión da `Connection timed out`: en EC2 → grupo de seguridad → reglas de entrada, cambiar el origen de SSH a «Mi IP». A quien usa la web no le afecta.

### 5.3 Cómo repetir el despliegue

```bash
# En la máquina (Ubuntu 24.04), una vez:
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2 docker-buildx
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu   # después, salir (exit) y volver a entrar
git clone https://github.com/albertoieszaidinvergeles/planificador-itinerarios.git
```

```powershell
# En tu ordenador: copiar el .env sin pegar la clave en ningún sitio
scp -i "$env:USERPROFILE\.ssh\labsuser.pem" infra\.env ubuntu@<IP-ELASTICA>:~/planificador-itinerarios/infra/.env
```

```bash
# En la máquina: DOMINIO con la IP elástica separada por guiones
cd ~/planificador-itinerarios/infra
sed -i 's|^DOMINIO=.*|DOMINIO=<IP-CON-GUIONES>.sslip.io|' .env && chmod 600 .env
docker compose up -d --build
```

**Actualizar a una versión nueva:** `git pull && docker compose up -d --build` desde `infra/`.

**Clerk en EC2 usa la instancia de desarrollo** (`pk_test_`, por eso se ve la marca *Development mode*): funciona en cualquier dirección, sin proxy ni clave secreta (`CLERK_SECRET_KEY` no está en el servidor). La instancia de producción está ligada al dominio de Vercel.

## 6. Problemas de despliegue (añadir cuando ocurran)

| Fecha | Problema | Causa | Solución |
|---|---|---|---|
| | | | |
