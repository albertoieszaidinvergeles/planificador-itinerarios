# Despliegues — Vercel, Clerk, Docker y AWS EC2

> URLs y valores concretos se añaden al ejecutarlos. **Sin secretos**: aquí solo configuración
> no secreta, comandos y evidencias.

## 1. URLs (estado de la entrega)

| App | Capa | URL | Fecha | Versión Git | Estado |
|---|---|---|---|---|---|
| App 1 | frontend Vercel | _(pendiente)_ | | | ⬜ H7 |
| App 1 | backend Vercel | _(pendiente)_ | | | ⬜ H7 |
| App 2 | frontend Vercel | _(pendiente)_ | | | ⬜ H10 |
| App 2 | backend Vercel | _(pendiente)_ | | | ⬜ H10 |
| App 2 | EC2 (Docker, HTTPS) | _(pendiente)_ | | | ⬜ H11 |

## 2. Vercel — dos proyectos por aplicación

| Proyecto | Raíz | Publica | Variables |
|---|---|---|---|
| `app1-frontend` | `app1/frontend` | estáticos de Vite (`dist/`) | `VITE_API_BASE_URL` (pública) |
| `app1-backend` | `app1/backend` | FastAPI (runtime Python, `main.py` exporta `app`) | `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT` + origen CORS del frontend |
| `app2-frontend` | `app2/frontend` | estáticos de Vite | `VITE_API_BASE_URL`, `VITE_CLERK_PUBLISHABLE_KEY` |
| `app2-backend` | `app2/backend` | FastAPI | claves de IA + `CLERK_SECRET_KEY` (si la integración la requiere) + CORS con `Authorization` |

### 2.1 Procedimiento CLI (reproducible)

```bash
npm install -g vercel && vercel --version
vercel login
vercel link                       # desde la raíz del proyecto correspondiente
vercel env add AI_API_KEY         # introducir el valor de forma interactiva (nunca en el historial)
vercel deploy
vercel deploy --prod
```

- Distinguir **Development / Preview / Production**; cambiar variables implica volver a desplegar.
- Comprobar preflight y cabeceras CORS del backend contra el origen real del frontend.

### 2.2 Comprobación de cierre (ambas apps en Vercel)

- [ ] URL pública correcta en ambos proyectos.
- [ ] Caso válido → `200` con JSON desde la URL desplegada.
- [ ] Caso de error (422 o 502 simulado) visible en la misma pantalla.
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
