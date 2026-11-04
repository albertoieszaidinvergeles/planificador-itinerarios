# Planificador de itinerarios — PR01-UD1

**[🇬🇧 English version below](#english-version)**

**Necesidad:** una persona que visita una ciudad quiere ideas sencillas para organizar un día. Introduce ciudad, fecha, número de personas y gustos, y la mini aplicación web le devuelve un plan de un día usando **una API de inteligencia artificial**, en **una sola pantalla**.  

**Asignatura:** Desarrollo de componentes software para sistemas de aprendizaje automático · UD1 «Mini aplicación web con una API de IA».
**Miembros:** Alberto Ortiz Sánchez y Manuel Montalban Arco

> **Regla de alcance:** una sola pantalla, un solo formulario, una sola función útil y una sola API de IA (OpenRouter). **Cero persistencia** (sin BD, sin `localStorage`), sin CRUD y sin pantallas adicionales. Ver [`docs/ERS.md`](docs/ERS.md).

---

## 📑 Índice / Table of Contents
- [Planificador de itinerarios — PR01-UD1](#planificador-de-itinerarios--pr01-ud1)
  - [📑 Índice / Table of Contents](#-índice--table-of-contents)
  - [Las dos aplicaciones](#las-dos-aplicaciones)
  - [Estructura del repositorio](#estructura-del-repositorio)
  - [Variables de entorno (sin valores secretos)](#variables-de-entorno-sin-valores-secretos)
  - [Instalación y ejecución](#instalación-y-ejecución)
  - [Pruebas](#pruebas)
  - [URLs (despliegues)](#urls-despliegues)
  - [Documentación](#documentación)
  - [Hitos de la entrega](#hitos-de-la-entrega)
  - [Presentación (para la defensa)](#presentación-para-la-defensa)
- [Itinerary Planner — PR01-UD1 (English Version)](#itinerary-planner--pr01-ud1-english-version)
  - [The Two Applications](#the-two-applications)
  - [Repository Structure](#repository-structure)
  - [Environment Variables (Safe / No Secrets)](#environment-variables-safe--no-secrets)
  - [Installation \& Execution](#installation--execution)
  - [Testing](#testing)
  - [Deployment URLs](#deployment-urls)

---

## Las dos aplicaciones  
  
| | **App 1** | **App 2** |
|---|---|---|
| **Proceso** | Construcción manual e incremental del equipo | Proyecto nuevo desde cero con **GitHub Spec Kit** + asistencia de IA |
| **Identidad** | Sin Clerk | **Clerk** (acceso con Google, modal en la misma SPA, token verificado en backend) |
| **Despliegue** | **Vercel** (frontend y backend) | **Vercel** (frontend, API y Clerk) + **Docker en AWS EC2** |
| **Código** | `app1/` | `app2/` (frontend y backend implementados según la spec) |

## Estructura del repositorio  

```text
planificador-itinerarios/
├── README.md                                        # este archivo / this file
├── docs/
│   ├── ERS.md            # ERS (entregable «ERS», plantilla del docente)
│   ├── evidencias/figma/ # bocetos de Figma (solo referencia visual, ver ERS Anexo B)
│   ├── planificador-itinerarios-documento-tecnico.md  # documento técnico v3 (arquitectura, contrato, despliegues)
│   ├── proceso.md        # decisiones e incidencias (a medida que ocurren)
│   ├── pruebas.md        # cómo se ejecutan, matriz y prueba real documentada
│   ├── comparativa.md    # App 1 vs App 2 (tiempo, calidad, errores, mantenibilidad, IA)
│   ├── despliegues.md    # URLs, Vercel CLI, Clerk, Docker y EC2
│   └── uso-ia.md         # registro crítico del uso de IA
├── app1/
│   ├── backend/          # main.py (app = FastAPI()), ia.py, requirements.txt, .env.example, tests/
│   └── frontend/         # Vue 3 + Vite + Tailwind (SPA única)
├── app2/                 # .specify/ · specs/ · backend/ · frontend/ · API y proxy Clerk para Vercel
├── infra/                # Dockerfile.backend · Dockerfile.frontend · compose.yaml · .env.example · proxy/
└── presentacion/         # defensa.pptx
```

> Toda la documentación vive en `docs/`, con la ERS en `docs/ERS.md` como exige el enunciado. Las carpetas de código se crean al empezar cada fase.

## Variables de entorno (sin valores secretos)

| Variable | Dónde | Entorno | Descripción |
|---|---|---|---|
| `AI_API_KEY` | backend | secreta | Clave de OpenRouter. **Solo backend** (Vercel/EC2). Nunca en el frontend ni en git |
| `AI_MODEL` | backend | configuración | Modelo actual `nvidia/nemotron-3.5-lightning:free`; Vercel aún requiere actualizarlo |
| `AI_TIMEOUT` | backend | configuración | Segundos de espera al proveedor (20) |
| `VITE_API_BASE_URL` | frontend | **pública** | URL HTTPS del backend desplegado |
| `CLERK_SECRET_KEY` | backend App 2 | secreta | Variable del ejemplo de configuración; la verificación actual usa el JWKS público |
| `CLERK_ISSUER` | backend App 2 | configuración | Emisor Clerk obligatorio para comprobar firma y `iss` |
| `CLERK_AUDIENCE` | backend App 2 | configuración | Audiencia opcional del token; si se configura, se valida |
| `VITE_CLERK_PUBLISHABLE_KEY` | frontend App 2 | **pública** | Clave publishable de Clerk (pública por diseño) |

Se distribuyen como `.env.example` con **nombres y valores ficticios**; los `.env` reales están en `.gitignore` y fuera de las imágenes Docker.

## Instalación y ejecución

**Prerrequisitos:** Python 3.10+, Node.js/npm, Git; `uv` para instalar Spec Kit y Docker solo para la fase final de App 2.

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

# ── App 2: Spec Kit (ya inicializado con Copilot, versión 1.2.2) ─
uv tool install specify-cli==1.2.2
specify init app2 --integration copilot --force --non-interactive

# ── App 2: contenedores (fase final) ────────────────────────────
cd infra
docker compose build && docker compose up -d
docker compose ps && docker compose logs
docker compose down
```

## Pruebas

```powershell
# App 1 (desde la raíz del repositorio)
cd app1\backend
pytest -v
```

```powershell
# App 2 (desde la raíz del repositorio; con el entorno ya preparado)
Set-Location app2\backend
.\.venv\Scripts\python.exe -m pytest -v
```

La suite cubre: entrada válida (una sola llamada al mock), entrada inválida (422 sin llamar a la IA), límites de longitud, fallo del proveedor (502) y timeout (504); en App 2 se añaden los rechazos de Clerk (401). Última ejecución automatizada de App 2: **45 passed** el 29/10/2026.

## URLs (despliegues)

| Aplicación | Capa | URL | Estado |
|---|---|---|---|
| App 1 | Vercel | ACABADA | https://planificador-itinerarios-iota.vercel.app/ |
| App 2 | Vercel | [planificador-itinerarios.vercel.app](https://planificador-itinerarios.vercel.app/) | ✅ H10 — web y API desplegadas; prueba autenticada confirmada |
| App 2 | EC2 (Docker, HTTPS) | [107-20-112-76.sslip.io](https://107-20-112-76.sslip.io/) | ✅ H11 — responde mientras el Learner Lab esté iniciado |

## Documentación

| Documento | Contenido |
|---|---|
| [Documento técnico](docs/planificador-itinerarios-documento-tecnico.md) | Restricciones, idea, arquitectura, contrato HTTP, App 1, App 2 (Spec Kit + Clerk), Docker/EC2, seguridad, hitos Git y mapa de la rúbrica |
| [ERS](docs/ERS.md) | Especificación de requisitos según plantilla: OBJ, RES, 5 RF + 4 RNF con criterios de aceptación, trazabilidad y Anexo C (Clerk) |
| [docs/proceso.md](docs/proceso.md) | Decisiones e incidencias a medida que ocurren |
| [docs/pruebas.md](docs/pruebas.md) | Matriz de pruebas, comandos y prueba real documentada |
| [docs/comparativa.md](docs/comparativa.md) | Comparación App 1 vs App 2 con evidencias y tiempos aproximados |
| [docs/despliegues.md](docs/despliegues.md) | Vercel, API serverless, proxy Clerk, CLI, Docker y EC2 |
| [docs/uso-ia.md](docs/uso-ia.md) | Registro del uso de IA: qué se aceptó, qué se rechazó, verificación humana |

## Hitos de la entrega

H0 inicio · H1 backend mínimo · H2 contrato y errores · H3 pruebas · H4 frontend · H5 integración · H6 Tailwind y revisión · **H7 Vercel App 1** · H8 Spec Kit · H9 App 2 · **H10 Clerk + Vercel App 2 (desplegado)** · **H11 Docker + EC2** · H12 cierre (comparativa y presentación).

## Presentación (para la defensa)
`presentacion/defensa.pptx` — Estructura recomendada para la defensa ante el docente.

---

<div id="english-version"></div>

# Itinerary Planner — PR01-UD1 (English Version)

**Need:** A city visitor wants simple ideas to organize a single day. They input the city, date, number of people, and preferences, and the web mini-app returns a one-day plan using **an AI API**, all on **a single screen**.

**Course:** Software Component Development for Machine Learning Systems · UD1 "Mini web application with an AI API".
**Team:** Alberto Ortiz Sánchez and Manuel Montalban Arco

> **Scope Rule:** A single screen, a single form, a single useful function, and a single AI API (OpenRouter). **Zero persistence** (no database, no `localStorage`), no CRUD operations, and no extra screens. See [`docs/ERS.md`](docs/ERS.md).

---

## The Two Applications

| | **App 1** | **App 2** |
|---|---|---|
| **Process** | Manual and incremental team construction | Brand new project from scratch using **GitHub Spec Kit** + AI assistance |
| **Identity** | Without Clerk | **Clerk** (Google authentication, modal inside the SPA, token verified in backend) |
| **Deployment** | **Vercel** (frontend and backend) | **Vercel** (frontend, API, and Clerk) + **Docker on AWS EC2** |
| **Code** | `app1/` | `app2/` (frontend and backend implemented according to specs) |

## Repository Structure

*(See the Spanish file tree above for the identical folder structure).*

## Environment Variables (Safe / No Secrets)

| Variable | Target | Environment | Description |
|---|---|---|---|
| `AI_API_KEY` | Backend | Secret | OpenRouter API key. **Backend only** (Vercel/EC2). Never exposed in frontend or Git. |
| `AI_MODEL` | Backend | Config | Current model: `nvidia/nemotron-3.5-lightning:free`. |
| `AI_TIMEOUT` | Backend | Config | Provider timeout in seconds (20). |
| `VITE_API_BASE_URL` | Frontend | **Public** | HTTPS URL of the deployed backend. |
| `CLERK_SECRET_KEY` | App 2 Backend | Secret | Config template variable; current verification relies on public JWKS. |
| `CLERK_ISSUER` | App 2 Backend | Config | Mandatory Clerk issuer to verify signature and `iss`. |
| `VITE_CLERK_PUBLISHABLE_KEY` | App 2 Frontend | **Public** | Clerk publishable key. |

## Installation & Execution

**Prerequisites:** Python 3.10+, Node.js/npm, Git; `uv` for Spec Kit installation and Docker for the final deployment phase of App 2.

```bash
# ── App 1: Backend ──────────────────────────────────────────────
cd app1/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # Fill in AI_API_KEY, AI_MODEL, AI_TIMEOUT
uvicorn main:app --reload                           # http://127.0.0.1:8000

# ── App 1: Frontend (Separate terminal) ─────────────────────────
cd app1/frontend
npm install
cp .env.example .env                                # VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev                                         # http://localhost:5173
```

## Testing

```powershell
# App 1 Backend Tests
cd app1\backend
pytest -v
```
The test suite validates: valid input (single mock call), invalid input (422 status without calling AI), length limits, provider failures (502), and timeouts (504). App 2 additionally validates Clerk access rejections (401).

## Deployment URLs

| Application | Layer | URL | Status |
|---|---|---|---|
| App 1 | Vercel | COMPLETED | https://planificador-itinerarios-iota.vercel.app/ |
| App 2 | Vercel | [planificador-itinerarios.vercel.app](https://planificador-itinerarios.vercel.app/) | ✅ H10 — Web & API deployed; authenticated test confirmed |
| App 2 | EC2 (Docker, HTTPS) | [107-20-112-76.sslip.io](https://107-20-112-76.sslip.io/) | ✅ H11 — available while the Learner Lab session is running |
