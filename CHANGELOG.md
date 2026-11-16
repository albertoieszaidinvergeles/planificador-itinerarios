# Registro de cambios / Changelog

Todos los cambios notables de este proyecto se documentan en este archivo, en **español e inglés**.
*All notable changes to this project are documented in this file, in **Spanish and English**.*

Formato basado en [Keep a Changelog 1.1.0](https://keepachangelog.com/es/1.1.0/) y versiones
siguiendo [Semantic Versioning](https://semver.org/lang/es/).
*Based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).*

> **Nota:** todavía no hay etiquetas (`git tag`) publicadas; el detalle commit a commit, con
> autor, hito y tiempo, está en [`docs/changelog.md`](docs/changelog.md).
> *Note: no tags are published yet; the commit-by-commit log with author, milestone, and time is
> in [`docs/changelog.md`](docs/changelog.md).*

## [1.0.0] - 2026-11-16

### Añadido / Added

- **App 2 completa** según GitHub Spec Kit: backend con autenticación **Clerk** (Bearer/JWKS,
  firma RS256) y frontend terminado (24/24 tareas) con modal de acceso en la misma SPA.
  *Complete **App 2** with GitHub Spec Kit: backend with **Clerk** authentication (Bearer/JWKS,
  RS256 signature) and finished frontend (24/24 tasks) with a sign-in modal inside the same SPA.*
- **Despliegues de App 2:** Vercel (función ASGI para `/api/plan` y proxy `/__clerk`) y
  **AWS EC2 con Docker** (Caddy, HTTPS con Let's Encrypt en `sslip.io`).
  *App 2 deployments: Vercel (ASGI function for `/api/plan` and `/__clerk` proxy) and
  **AWS EC2 with Docker** (Caddy, HTTPS via Let's Encrypt on `sslip.io`)*
- **Presentación de la defensa:** diapositivas, PDF y guion en [`presentacion/`](presentacion/).
  *Defense presentation: slides, PDF, and script in [`presentacion/`](presentacion/)*
- **Archivos de comunidad de GitHub:** [`METAS.md`](METAS.md), este `CHANGELOG.md`,
  [`LICENSE`](LICENSE) (MIT), [`CONTRIBUTING.md`](CONTRIBUTING.md),
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`SECURITY.md`](SECURITY.md) y plantillas de
  issues/PR en [`.github/`](.github/).
  *GitHub community files: [`METAS.md`](METAS.md), this `CHANGELOG.md`, [`LICENSE`](LICENSE) (MIT),
  [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md),
  [`SECURITY.md`](SECURITY.md), and issue/PR templates in [`.github/`](.github/)*

### Cambiado / Changed

- **Modelo de IA:** `nvidia/nemotron-3-super-120b-a12b:free` → `nvidia/nemotron-3.5-lightning:free`
  tras el retiro de OpenRouter del modelo anterior (29/10); 5/5 llamadas reales en `200`.
  *AI model switched after OpenRouter retired the previous free model; 5/5 real calls returned `200`.*
- **`.env.example`** actualizado en App 1 y App 2 con el nuevo modelo.
  *`.env.example` updated in App 1 and App 2 with the new model.*

### Corregido / Fixed

- **`AI_MODEL` actualizado en Vercel** a `nvidia/nemotron-3.5-lightning:free`: la App 1 respondía
  `502` en producción; verificado con una petición real el 16/11/2026 → `200`.
  *AI model updated on Vercel to `nvidia/nemotron-3.5-lightning:free`: App 1 was returning `502` in
  production; verified with a real request on 2026-11-16 → `200`.*

### Seguridad / Security

- **App 2:** tokens de Clerk verificados en backend antes de validar la entrada; sin secretos en
  el bundle del frontend; proxy de Clerk que reenvía la IP del visitante.
  *App 2: Clerk tokens verified in the backend before validating input; no secrets in the
  frontend bundle; Clerk proxy forwards the visitor's IP.*
- **App 1:** saneado anti-inyección de prompt (`formato.py`), `/docs` cerrado en producción,
  cabeceras de seguridad y rate limit en el WAF de Vercel (`429`).
  *App 1: prompt-injection sanitizing (`formato.py`), `/docs` disabled in production, security
  headers, and rate limiting on Vercel's WAF (`429`).*

## [0.2.0] - 2026-10-20

### Añadido / Added

- **App 1 desplegada en Vercel** (H7): frontend y backend en el mismo origen, favicon y
  Vercel Web Analytics (sin cookies ni `localStorage`).
  *App 1 deployed on Vercel (H7): frontend and backend on the same origin, favicon, and Vercel
  Web Analytics (no cookies or `localStorage`).*
- **IA sin alucinaciones:** reglas anti-alucinación en el mensaje `system`, `temperature 0.2` y
  variación aleatoria por petición (`ENFOQUES`/`TOQUES` + `seed`), sin memoria ni estado.
  *Hallucination-free AI: anti-hallucination rules in the `system` message, `temperature 0.2`, and
  random per-request variation (`ENFOQUES`/`TOQUES` + `seed`), with no memory or state.*
- **Pruebas reales de la IA:** 6 peticiones a `/api/plan` en producción, todas `200`, documentadas
  en [`docs/pruebas.md`](docs/pruebas.md).
  *Real AI tests: 6 requests to `/api/plan` in production, all `200`, documented in
  [`docs/pruebas.md`](docs/pruebas.md).*

### Corregido / Fixed

- Formato fijo `Mañana:`/`Tarde:`/`Noche:` en la respuesta de la IA para las tarjetas del
  frontend (sin introducción ni recuento de palabras).
  *Fixed `Morning:`/`Afternoon:`/`Night:` response format for the frontend cards (no intro or
  word counts).*

## [0.1.0] - 2026-10-16

### Añadido / Added

- **Backend App 1 (H1–H2):** FastAPI con `POST /api/plan`, validación de entrada, contrato
  `200/422/502/504/500` y llamada única a OpenRouter.
  *App 1 backend (H1–H2): FastAPI with `POST /api/plan`, input validation, `200/422/502/504/500`
  contract, and a single call to OpenRouter.*
- **Frontend App 1 (H4–H6):** Vue 3 + Vite + Tailwind, formulario único con los cuatro estados de
  la pantalla (entrada, espera, resultado, error), tema oscuro/claro y responsive.
  *App 1 frontend (H4–H6): Vue 3 + Vite + Tailwind, single form with the four screen states
  (input, waiting, result, error), dark/light theme, and responsive layout.*
- **Pruebas (H3):** suite de pytest con la IA simulada (entradas válidas e inválidas, límites,
  `502` y `504`); 41 tests en verde el 17/10.
  *Tests (H3): pytest suite with mocked AI (valid and invalid input, limits, `502`, and `504`);
  41 tests green on 17 October.*
- **Documentación:** [`docs/ERS.md`](docs/ERS.md) v2.1, [`docs/pruebas.md`](docs/pruebas.md),
  [`docs/proceso.md`](docs/proceso.md) y [`docs/changelog.md`](docs/changelog.md).
  *Documentation: [`docs/ERS.md`](docs/ERS.md) v2.1, [`docs/pruebas.md`](docs/pruebas.md),
  [`docs/proceso.md`](docs/proceso.md), and [`docs/changelog.md`](docs/changelog.md).*

### Seguridad / Security

- `/docs` solo con `DOCS_ACTIVOS=1`, cabeceras de seguridad por middleware y
  `--no-server-header`.
  *`/docs` only with `DOCS_ACTIVOS=1`, security headers via middleware, and `--no-server-header`.*

## [0.0.1] - 2026-10-08

### Añadido / Added

- **Inicio del proyecto (H0):** [`README.md`](README.md), documento técnico v3,
  [`docs/ERS.md`](docs/ERS.md) v1.0/2.0, [`docs/PropuestaFases.md`](docs/PropuestaFases.md) y
  [`docs/ResumenEnunciado.md`](docs/ResumenEnunciado.md).
  *Project kickoff (H0): [`README.md`](README.md), technical document v3,
  [`docs/ERS.md`](docs/ERS.md) v1.0/2.0, [`docs/PropuestaFases.md`](docs/PropuestaFases.md), and
  [`docs/ResumenEnunciado.md`](docs/ResumenEnunciado.md).*

[1.0.0]: https://github.com/albertoieszaidinvergeles/planificador-itinerarios/commits/main
[0.2.0]: https://github.com/albertoieszaidinvergeles/planificador-itinerarios/commits/main
[0.1.0]: https://github.com/albertoieszaidinvergeles/planificador-itinerarios/commits/main
[0.0.1]: https://github.com/albertoieszaidinvergeles/planificador-itinerarios/commits/main
