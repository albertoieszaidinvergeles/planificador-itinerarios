# Planificador de itinerarios — PR01-UD1

**Necesidad:** una persona que visita una ciudad quiere ideas sencillas para organizar un
día. Introduce ciudad, fecha, número de personas y gustos, y la mini aplicación web le
devuelve un plan de un día usando **una API de inteligencia artificial**, en **una sola
pantalla**.

**Asignatura:** Desarrollo de componentes software para sistemas de aprendizaje automático · UD1 «Mini aplicación web con una API de IA».
**Miembros:** Alberto Ortiz Sánchez y Manuel Montalban Arco

> **Regla de alcance:** una sola pantalla, un solo formulario, una sola función útil y una
> sola API de IA (OpenRouter). **Cero persistencia** (sin BD, sin `localStorage`), sin CRUD
> y sin pantallas adicionales. Ver [`docs/ERS.md`](docs/ERS.md).

## Las dos aplicaciones

| | **App 1** | **App 2** |
|---|---|---|
| Proceso | Construcción manual e incremental del equipo | Proyecto nuevo desde cero con **GitHub Spec Kit** + asistencia de IA |
| Identidad | Sin Clerk | **Clerk** (acceso con Google, modal en la misma SPA, token verificado en backend) |
| Despliegue | **Vercel** (frontend y backend) | **Vercel** (demo de Clerk) + **Docker en AWS EC2** (definitivo) |
| Código | `app1/` | `app2/` (carpeta vacía al inicio; spec antes que código) |

## Estructura del repositorio

```text
planificador-itinerarios/
├── README.md                                        # este archivo
├── Figma/                                           # bocetos de la pantalla única
├── docs/
│   ├── ERS.md            # ERS (entregable «ERS», plantilla del docente)
│   ├── planificador-itinerarios-documento-tecnico.md  # documento técnico v3 (arquitectura, contrato, despliegues)
│   ├── proceso.md        # decisiones e incidencias (a medida que ocurren)
│   ├── pruebas.md        # cómo se ejecutan, matriz y prueba real documentada
│   ├── comparativa.md    # App 1 vs App 2 (tiempo, calidad, errores, mantenibilidad, IA)
│   ├── despliegues.md    # URLs, Vercel CLI, Clerk, Docker y EC2
│   └── uso-ia.md         # registro crítico del uso de IA
├── app1/
│   ├── backend/          # main.py (app = FastAPI()), ia.py, requirements.txt, .env.example, tests/
│   └── frontend/         # Vue 3 + Vite + Tailwind (SPA única)
├── app2/                 # .specify/ · specs/ · backend/ · frontend/   (nuevo desde cero)
├── infra/                # Dockerfile.backend · Dockerfile.frontend · compose.yaml · .env.example · proxy/
└── presentacion/         # defensa.pptx
```

> Toda la documentación vive en `docs/`, con la ERS en `docs/ERS.md` como exige el
> enunciado. Las carpetas de código se crean al empezar cada fase.

## Variables de entorno (sin valores secretos)

| Variable | Dónde | Entorno | Descripción |
|---|---|---|---|
| `AI_API_KEY` | backend | secreta | Clave de OpenRouter. **Solo backend** (Vercel/EC2). Nunca en el frontend ni en git |
| `AI_MODEL` | backend | configuración | Modelo `:free` a usar (documentar el elegido) |
| `AI_TIMEOUT` | backend | configuración | Segundos de espera al proveedor (20) |
| `VITE_API_BASE_URL` | frontend | **pública** | URL HTTPS del backend desplegado |
| `CLERK_SECRET_KEY` | backend App 2 | secreta | Clave secreta de Clerk (solo App 2) |
| `VITE_CLERK_PUBLISHABLE_KEY` | frontend App 2 | **pública** | Clave publishable de Clerk (pública por diseño) |

Se distribuyen como `.env.example` con **nombres y valores ficticios**; los `.env` reales
están en `.gitignore` y fuera de las imágenes Docker.

## Instalación y ejecución

**Prerrequisitos:** Python 3.10+, Node.js/npm, Git; Docker solo para la fase de App 2.

```bash
# ── App 1: backend ──────────────────────────────────────────────
cd app1/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # rellena AI_API_KEY, AI_MODEL, AI_TIMEOUT
uvicorn main:app --reload                           # http://127.0.0.1:8000

# ── App 1: frontend (otra terminal) ─────────────────────────────
cd app1/frontend
npm install
cp .env.example .env                                # VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev                                         # http://localhost:5173

# ── App 2: especificación (ANTES de escribir código) ────────────
# Instalar GitHub Spec Kit oficial con un agente compatible y anotar versión.
# Generar: /speckit.constitution · /speckit.specify · /speckit.clarify
#          /speckit.plan · /speckit.tasks · /speckit.analyze
# Artefactos en app2/specs/ — su commit debe ser ANTERIOR al primer código.

# ── App 2: contenedores (fase final) ────────────────────────────
cd infra
docker compose build && docker compose up -d
docker compose ps && docker compose logs
docker compose down
```

## Pruebas

```bash
cd app1/backend && pytest -v        # la IA está simulada: no consume créditos ni internet
```

La suite cubre: entrada válida (una sola llamada al mock), entrada inválida (422 sin llamar
a la IA), límites de longitud, fallo del proveedor (502) y timeout (504); en App 2 se añaden
los rechazos de Clerk (401). Matriz y prueba real documentada en [`docs/pruebas.md`](docs/pruebas.md).

## URLs (despliegues)

| Aplicación | Capa | URL | Estado |
|---|---|---|---|
| App 1 | frontend Vercel | _(pendiente)_ | ⬜ H7 |
| App 1 | backend Vercel | _(pendiente)_ | ⬜ H7 |
| App 2 | frontend Vercel | _(pendiente)_ | ⬜ H10 |
| App 2 | backend Vercel | _(pendiente)_ | ⬜ H10 |
| App 2 | EC2 (Docker, HTTPS) | _(pendiente)_ | ⬜ H11 |

Toda la configuración reproducible (CLI, variables, CORS, Clerk, Docker, EC2) está en
[`docs/despliegues.md`](docs/despliegues.md).

## Documentación

| Documento | Contenido |
|---|---|
| [Documento técnico](docs/planificador-itinerarios-documento-tecnico.md) | Restricciones, idea, arquitectura, contrato HTTP, App 1, App 2 (Spec Kit + Clerk), Docker/EC2, seguridad, hitos Git y **mapa de la rúbrica** |
| [ERS](docs/ERS.md) | Especificación de requisitos según plantilla: OBJ, RES, 5 RF + 4 RNF con criterios de aceptación, trazabilidad y Anexo C (Clerk) |
| [docs/proceso.md](docs/proceso.md) | Decisiones e incidencias a medida que ocurren |
| [docs/pruebas.md](docs/pruebas.md) | Matriz de pruebas, comandos y prueba real documentada |
| [docs/comparativa.md](docs/comparativa.md) | Comparación App 1 vs App 2 con evidencias |
| [docs/despliegues.md](docs/despliegues.md) | Vercel (2 proyectos por app), CLI, Clerk, Docker y EC2 |
| [docs/uso-ia.md](docs/uso-ia.md) | Registro del uso de IA: qué se aceptó, qué se rechazó, verificación humana |
| [Propuesta de fases](docs/PropuestaFases.pdf) | Planificación por fases del proyecto |
| [Resumen del enunciado](docs/ResumenEnunciado.pdf) | Resumen de los requisitos de la práctica |

## Hitos de la entrega

H0 inicio · H1 backend mínimo · H2 contrato y errores · H3 pruebas · H4 frontend ·
H5 integración · H6 Tailwind y revisión · **H7 Vercel App 1** · H8 Spec Kit · H9 App 2 ·
**H10 Clerk + Vercel App 2** · **H11 Docker + EC2** · H12 cierre (comparativa y presentación).

## Presentación (para la defensa)

`presentacion/defensa.pptx` — estructura recomendada: problema y límite de alcance ·
arquitectura y contrato · ERS y decisiones · evolución App 1 · Spec Kit y App 2 ·
pruebas y seguridad · Vercel y EC2 · comparativa y conclusiones. Demo mínima: entrada
válida, error controlado, rechazo 401 sin token, App 2 en EC2 y un test con mock.
