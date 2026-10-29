# App 2 — Planificador de itinerarios (Spec Kit + Clerk)

Constitución del equipo para la App 2. Tiene prioridad sobre cualquier instrucción
que pida una herramienta o un agente: si algo contradice aquí, se cambia la
instrucción, no la constitución.

## Principios fundamentales

### I. El contrato no se toca (NO NEGOCIABLE)
El endpoint es `POST /api/plan` con la misma entrada (`ciudad`, `fecha`, `personas`,
`gustos`) y los mismos códigos y cuerpos de error que la App 1 (`422`, `502`,
`504`, `500` con `codigo` + `mensaje`). La App 2 solo **añade** el `401 NO_AUTENTICADO`.
Ningún cambio de diseño puede romper este contrato: lo comprueban los tests.

### II. Cero secretos en el repositorio ni en la documentación
Toda clave vive en `.env` (ignorado por Git) o en las variables de entorno de Vercel.
`.env.example` solo con nombres y placeholders. Ni claves, ni tokens, ni capturas con
secretos, ni valores reales en `docs/`. La secret de Clerk (`sk_…`) jamás aparece en el
frontend, en el bundle compilado ni en el historial de Git.

### III. Identidad externa, sin usuarios propios
La autenticación es **solo Clerk** (acceso con Google, componente modal en la única
pantalla): nada de tablas de usuarios, contraseñas, roles ni páginas de login. El
**backend verifica el session token** (firma contra JWKS + emisor + caducidad +
audiencia) y responde `401 NO_AUTENTICADO` **antes** de consultar la IA. «Login bonito
pero backend abierto» es un fallo de la rúbrica.

### IV. Pruebas primero y sin conexión
TDD: se escribe el test antes que el código que lo cumple. La suite `pytest` pasa
**sin internet y sin créditos**: la IA y Clerk se sustituyen por mocks. Nada que
consulta servicios reales en CI ni en `pytest`. Se ejecuta `pytest` antes de cada
commit de backend y se anota el resultado en `docs/pruebas.md`.

### V. Entorno limpio: nada instala fuera de su sitio
- Python: **siempre en el entorno virtual del proyecto** (`app2/backend/.venv`).
  Prohibido `pip install` global o `--user`.
- Dependencias de **ejecución** → `app2/backend/requirements.txt`; las de **prueba**
  (`pytest`) → `app2/backend/requirements-dev.txt`, para que la producción (Vercel) no
  instale paquetes de test. Misma separación que en la App 1.
- Node: dependencias solo en `app2/frontend/node_modules` (`npm i` con esa carpeta
  como raíz). Prohibido instalar paquetes globales.
- No se añaden herramientas, servicios ni extensiones que el enunciado no pida.

### VI. Una sola pantalla, sin estado fuera de memoria
Vue 3 + Vite **sin router, sin store, sin `localStorage` ni cachés/contadores en la
aplicación** (lo prohíbe el enunciado). El resultado vive en memoria hasta el siguiente
envío. El rate limit y los límites se aplican en el borde (Vercel), nunca en la app.

## Stack tecnológico

- **Backend:** FastAPI + Pydantic + `httpx` + `python-dotenv` + `pyjwt[crypto]`
  (verificación JWKS de Clerk), mocks con `pytest`; errores traducidos a los códigos
  del contrato.
- **Frontend:** Vue 3 + Vite + Tailwind v4, formulario único, modal de Clerk
  (publishable key con prefijo `VITE_`).
- **Despliegue:** Vercel (un proyecto con raíz `app2/`: estáticos + función Python) y
  AWS EC2 con Docker para el RNF-03.
- **Identidad:** Clerk (instancia development hasta el despliegue; JWKS en
  `https://<instancia>.clerk.accounts.dev/.well-known/jwks.json`).

## Flujo de trabajo

1. `/speckit.specify` → especificación de la funcionalidad (una sola: generar un plan).
2. `/speckit.clarify` → solo si hay ambigüedades reales; se responde y se sigue.
3. `/speckit.plan` → plan técnico; se revisa antes de continuar.
4. `/speckit.tasks` → lista de tareas ordenadas (tests incluidos).
5. `/speckit.implement` → código cumpliendo la constitución; `pytest` en verde.
6. `/speckit.analyze` y `/speckit.checklist` → puertas de revisión antes de darlo por bueno.

Todo cambio de contexto (decisión, incidencia, verificación) se registra en
`docs/proceso.md` y `docs/changelog.md`, y las pruebas en `docs/pruebas.md`.

## Gobernanza

- Esta constitución manda sobre cualquier instrucción de agente; su cambio requiere
  acuerdo del equipo y queda registrado en `docs/proceso.md`.
- El repositorio es la fuente de verdad: se trabaja en `main` con commits pequeños y
  el empuje lo hace el dueño del repositorio desde GitHub Desktop.
- Nada académico ni de plantilla en la interfaz de usuario: texto de usuario real.
