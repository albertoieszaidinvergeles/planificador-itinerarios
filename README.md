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
  - [Metas y comunidad](#metas-y-comunidad)
  - [Hitos de la entrega](#hitos-de-la-entrega)
  - [Presentación (para la defensa)](#presentación-para-la-defensa)
- [Itinerary Planner — PR01-UD1 (English Version)](#itinerary-planner--pr01-ud1-english-version)
  - [The Two Applications](#the-two-applications)
  - [Repository Structure](#repository-structure)
  - [Environment Variables (Safe / No Secrets)](#environment-variables-safe--no-secrets)
  - [Installation \& Execution](#installation--execution)
  - [Testing](#testing)
  - [Deployment URLs](#deployment-urls)
  - [Documentation](#documentation)
  - [Goals and Community](#goals-and-community)
  - [Milestones](#milestones)
  - [Presentation (for the Defense)](#presentation-for-the-defense)

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
├── README.md                 # este archivo / this file (ES + EN)
├── METAS.md                  # metas del proyecto / project goals (ES + EN)
├── CHANGELOG.md              # versiones y cambios / release notes (ES + EN)
├── LICENSE                   # licencia MIT / MIT license
├── CONTRIBUTING.md           # guía de contribución / contributing guide (ES + EN)
├── CODE_OF_CONDUCT.md        # código de conducta / code of conduct (ES + EN)
├── SECURITY.md               # política de seguridad / security policy (ES + EN)
├── .github/                  # plantillas de issues/PR · CI · Dependabot
├── docs/
│   ├── ERS.md            # ERS (entregable «ERS», plantilla del docente)
│   ├── evidencias/figma/ # bocetos de Figma (solo referencia visual, ver ERS Anexo B)
│   ├── planificador-itinerarios-documento-tecnico.md  # documento técnico v3 (arquitectura, contrato, despliegues)
│   ├── proceso.md        # decisiones e incidencias (a medida que ocurren)
│   ├── pruebas.md        # cómo se ejecutan, matriz y prueba real documentada
│   ├── comparativa.md    # App 1 vs App 2 (tiempo, calidad, errores, mantenibilidad, IA)
│   ├── despliegues.md    # URLs, Vercel CLI, Clerk, Docker y EC2
│   └── changelog.md      # registro detallado de cambios y tiempos por hito
├── app1/
│   ├── backend/          # main.py (app = FastAPI()), ia.py, requirements.txt, .env.example, tests/
│   └── frontend/         # Vue 3 + Vite + Tailwind (SPA única)
├── app2/                 # .specify/ · specs/ · backend/ · frontend/ · API y proxy Clerk para Vercel
├── infra/                # Dockerfile.backend · Dockerfile.frontend · compose.yaml · .env.example · proxy/
└── presentacion/         # PresentacionPlanificadorItinerarios.pptx · PDF · guion-diapositivas.md
```

> Toda la documentación vive en `docs/`, con la ERS en `docs/ERS.md` como exige el enunciado.
> **Pendiente:** `docs/uso-ia.md` (registro del uso de la IA), ver [Metas y comunidad](#metas-y-comunidad).

## Variables de entorno (sin valores secretos)

| Variable | Dónde | Entorno | Descripción |
|---|---|---|---|
| `AI_API_KEY` | backend | secreta | Clave de OpenRouter. **Solo backend** (Vercel/EC2). Nunca en el frontend ni en git |
| `AI_MODEL` | backend | configuración | Modelo actual `nvidia/nemotron-3.5-lightning:free` (actualizado en Vercel el 16/11/2026) |
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
.venv\Scripts\python.exe -m pytest -v
```

La suite cubre: entrada válida (una sola llamada al mock), entrada inválida (422 sin llamar a la IA), límites de longitud, fallo del proveedor (502) y timeout (504); en App 2 se añaden los rechazos de Clerk (401). Última ejecución documentada: App 1 **41 passed** (17/10/2026) y App 2 **45 passed** (29/10/2026); verificación local del 16/11/2026: **41** y **47 passed**. En cada pull request, [GitHub Actions](.github/workflows/ci.yml) repite ambas suites, construye los dos frontends y comprueba los enlaces de la documentación.

## URLs (despliegues)

| Aplicación | Capa | URL | Estado |
|---|---|---|---|
| App 1 | Vercel | ACABADA | https://planificador-itinerarios-iota.vercel.app/ |
| App 2 | Vercel | [planificador-itinerarios.vercel.app](https://planificador-itinerarios.vercel.app/) | ✅ H10 — web y API desplegadas; prueba autenticada confirmada |
| App 2 | EC2 (Docker, HTTPS) | [107-20-112-76.sslip.io](https://107-20-112-76.sslip.io/) | ✅ H11 — responde mientras el Learner Lab esté iniciado |

> ✅ **Actualizado y verificado (16/11/2026):** `AI_MODEL` ya vale `nvidia/nemotron-3.5-lightning:free` en Vercel y una petición real a `POST /api/plan` en producción responde `200` con el plan. Historial en [`docs/proceso.md`](docs/proceso.md), sección «Problemas abiertos».

## Documentación

| Documento | Contenido |
|---|---|
| [Documento técnico](docs/planificador-itinerarios-documento-tecnico.md) | Restricciones, idea, arquitectura, contrato HTTP, App 1, App 2 (Spec Kit + Clerk), Docker/EC2, seguridad, hitos Git y mapa de la rúbrica |
| [ERS](docs/ERS.md) | Especificación de requisitos según plantilla: OBJ, RES, 5 RF + 4 RNF con criterios de aceptación, trazabilidad y Anexo C (Clerk) |
| [docs/proceso.md](docs/proceso.md) | Decisiones e incidencias a medida que ocurren |
| [docs/pruebas.md](docs/pruebas.md) | Matriz de pruebas, comandos y prueba real documentada |
| [docs/comparativa.md](docs/comparativa.md) | Comparación App 1 vs App 2 con evidencias y tiempos aproximados |
| [docs/despliegues.md](docs/despliegues.md) | Vercel, API serverless, proxy Clerk, CLI, Docker y EC2 |
| [docs/changelog.md](docs/changelog.md) | Registro de cambios y tiempos por hito (fecha, autor, rama/PR) |
| `docs/uso-ia.md` (**pendiente**) | Registro del uso de IA: qué se aceptó, qué se rechazó, verificación humana |

## Metas y comunidad

| Documento | Contenido |
|---|---|
| [METAS.md](METAS.md) | Metas del proyecto (académicas, producto, calidad y proceso) y pendientes conocidos |
| [CHANGELOG.md](CHANGELOG.md) | Versiones y cambios destacados (formato Keep a Changelog, ES + EN) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cómo reportar errores y proponer cambios, regla de alcance y convenciones |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Contrato de Colaboradores 2.1 (versión canónica en inglés + traducción) |
| [SECURITY.md](SECURITY.md) | Política de seguridad: reporte de vulnerabilidades **vía GitHub** |
| [LICENSE](LICENSE) | Licencia **MIT** |
| [`.github/`](.github/) | Plantillas de issues (error, idea, documentación), plantilla de PR, workflow de CI y Dependabot |

> El CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) ejecuta en cada PR las suites de
> ambos backends, la compilación de ambos frontends y la comprobación de enlaces y anclas de todos
> los Markdown (script propio en [`.github/scripts/check_markdown_links.py`](.github/scripts/check_markdown_links.py)).

## Hitos de la entrega

H0 inicio · H1 backend mínimo · H2 contrato y errores · H3 pruebas · H4 frontend · H5 integración · H6 Tailwind y revisión · **H7 Vercel App 1** · H8 Spec Kit · H9 App 2 · **H10 Clerk + Vercel App 2 (desplegado)** · **H11 Docker + EC2** · H12 cierre (comparativa y presentación).

## Presentación (para la defensa)

- [`presentacion/PresentacionPlanificadorItinerarios.pptx`](presentacion/PresentacionPlanificadorItinerarios.pptx) — diapositivas de la defensa.
- [`presentacion/PresentacionPlanItinerarios.pdf`](presentacion/PresentacionPlanItinerarios.pdf) — versión en PDF.
- [`presentacion/guion-diapositivas.md`](presentacion/guion-diapositivas.md) — guion hablado diapositiva a diapositiva.

---

<div id="english-version"></div>

# Itinerary Planner — PR01-UD1 (English Version)

**[🇪🇸 Versión en español](#planificador-de-itinerarios--pr01-ud1)**

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

*(See the Spanish file tree above for the identical folder structure, including the community files
`METAS.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `.github/`.)*

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

The test suite validates: valid input (single mock call), invalid input (422 status without calling AI), length limits, provider failures (502), and timeouts (504); App 2 additionally validates Clerk access rejections (401). Last documented run: App 1 **41 passed** (2026-10-17) and App 2 **45 passed** (2026-10-29); local verification on 2026-11-16: **41** and **47 passed**. On every pull request, [GitHub Actions](.github/workflows/ci.yml) runs both suites, builds both frontends, and checks the documentation links.

## Deployment URLs

| Application | Layer | URL | Status |
|---|---|---|---|
| App 1 | Vercel | COMPLETED | https://planificador-itinerarios-iota.vercel.app/ |
| App 2 | Vercel | [planificador-itinerarios.vercel.app](https://planificador-itinerarios.vercel.app/) | ✅ H10 — Web & API deployed; authenticated test confirmed |
| App 2 | EC2 (Docker, HTTPS) | [107-20-112-76.sslip.io](https://107-20-112-76.sslip.io/) | ✅ H11 — available while the Learner Lab session is running |

> ✅ **Updated and verified (2026-11-16):** `AI_MODEL` is now `nvidia/nemotron-3.5-lightning:free` on Vercel, and a real `POST /api/plan` request in production returns `200` with the plan. History in [`docs/proceso.md`](docs/proceso.md), section "Open issues".

## Documentation

| Document | Contents |
|---|---|
| [Technical document](docs/planificador-itinerarios-documento-tecnico.md) | Constraints, idea, architecture, HTTP contract, App 1, App 2 (Spec Kit + Clerk), Docker/EC2, security, Git milestones, and rubric map |
| [SRS](docs/ERS.md) | Requirements specification per the template: OBJ, RES, 5 RF + 4 RNF with acceptance criteria, traceability, and Annex C (Clerk) |
| [docs/proceso.md](docs/proceso.md) | Decisions and issues as they happen |
| [docs/pruebas.md](docs/pruebas.md) | Test matrix, commands, and documented real test run |
| [docs/comparativa.md](docs/comparativa.md) | App 1 vs App 2 comparison with evidence and approximate times |
| [docs/despliegues.md](docs/despliegues.md) | Vercel, serverless API, Clerk proxy, CLI, Docker, and EC2 |
| [docs/changelog.md](docs/changelog.md) | Detailed change and time log per milestone (date, author, branch/PR) |
| `docs/uso-ia.md` (**pending**) | AI usage log: what was accepted, what was rejected, human verification |

## Goals and Community

| Document | Contents |
|---|---|
| [METAS.md](METAS.md) | Project goals (academic, product, quality, and process) and known gaps |
| [CHANGELOG.md](CHANGELOG.md) | Versions and notable changes (Keep a Changelog format, ES + EN) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to report bugs and propose changes, scope rule, and conventions |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Contributor Covenant 2.1 (canonical English + translation) |
| [SECURITY.md](SECURITY.md) | Security policy: vulnerability reports **via GitHub** |
| [LICENSE](LICENSE) | **MIT** license |
| [`.github/`](.github/) | Issue templates (bug, idea, docs), PR template, CI workflow, and Dependabot |

> The CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs on every PR: both backend
> suites, both frontend builds, and a link/anchor check across all Markdown files (custom script in
> [`.github/scripts/check_markdown_links.py`](.github/scripts/check_markdown_links.py)).

## Milestones

H0 start · H1 minimal backend · H2 contract and errors · H3 tests · H4 frontend · H5 integration · H6 Tailwind and review · **H7 Vercel App 1** · H8 Spec Kit · H9 App 2 · **H10 Clerk + Vercel App 2 (deployed)** · **H11 Docker + EC2** · H12 wrap-up (comparison and presentation).

## Presentation (for the Defense)

- [`presentacion/PresentacionPlanificadorItinerarios.pptx`](presentacion/PresentacionPlanificadorItinerarios.pptx) — defense slides.
- [`presentacion/PresentacionPlanItinerarios.pdf`](presentacion/PresentacionPlanItinerarios.pdf) — PDF version.
- [`presentacion/guion-diapositivas.md`](presentacion/guion-diapositivas.md) — slide-by-slide spoken script.
