# Metas del proyecto / Project Goals

**[🇬🇧 English version below](#english-version)**

> Metas del proyecto **Planificador de itinerarios** (PR01-UD1).
> La base formal de requisitos es la [`docs/ERS.md`](docs/ERS.md); el día a día está en
> [`docs/proceso.md`](docs/proceso.md); los cambios y tiempos, en [`CHANGELOG.md`](CHANGELOG.md)
> y [`docs/changelog.md`](docs/changelog.md).

## Meta general

Construir, desplegar y documentar **dos versiones** de una mini aplicación web de **una sola
pantalla** que devuelve un plan de un día usando **una única API de inteligencia artificial**,
siguiendo **dos procesos de desarrollo claramente distinguibles** (manual e incremental vs.
dirigido por especificaciones con GitHub Spec Kit + Clerk), con pruebas, evidencias, despliegues
reales y defensa ante el docente.

## Metas académicas (entrega PR01-UD1)

| # | Meta | Cómo se mide | Estado |
|---|---|---|---|
| M1 | Completar los hitos H0–H12 | [`docs/changelog.md`](docs/changelog.md) (registro por hito) | ✅ H0–H11 · 🔄 H12 (cierre) |
| M2 | ERS trazable con la rúbrica | [`docs/ERS.md`](docs/ERS.md) v2.1 (OBJ, RF, RNF, Anexo C) | ✅ |
| M3 | Comparar los dos procesos con evidencias | [`docs/comparativa.md`](docs/comparativa.md) | 🔄 parcial (fases de App 1 y errores pendientes) |
| M4 | Registro crítico del uso de la IA | `docs/uso-ia.md` | ⬜ pendiente (aún no creado) |
| M5 | Despliegues verificables | [`docs/despliegues.md`](docs/despliegues.md) + [URLs del README](README.md#urls-despliegues) | ✅ Vercel (App 1 y App 2) · ✅ EC2 con Docker |
| M6 | Pruebas automatizadas documentadas | [`docs/pruebas.md`](docs/pruebas.md) | ✅ App 1: 41 tests (17/10) · ✅ App 2: 45 tests (29/10) |
| M7 | Presentación y defensa | [`presentacion/`](presentacion/) | 🔄 guion y diapositivas listos |

## Metas de producto (OBJ-01 … OBJ-05 de la ERS)

| ID | Meta | Indicador de logro |
|---|---|---|
| OBJ-01 | Una sola función útil: entrada → plan de un día en la misma pantalla | Sin navegar a otra vista (CA-RF04-01) |
| OBJ-02 | Contrato HTTP claro y errores sin exponer detalles internos | 200/422/502/504/500 (y 401 en App 2) probados |
| OBJ-03 | Simplicidad: una pantalla, una API de IA, cero persistencia | Sin router, sin BD, sin `localStorage` (RNF-02) |
| OBJ-04 | Dos procesos de desarrollo distinguibles | H0–H7 (App 1) vs. artefactos de Spec Kit previos al código (App 2) |
| OBJ-05 | Despliegue y autenticación según el enunciado | Vercel; App 2 además con Clerk y Docker en AWS EC2 |

## Metas de calidad

- **Contrato:** validación en servidor, errores `422`/`502`/`504`/`500` (y `401` en App 2) con
  `{"error":{"codigo","mensaje"}}`; ningún fallo detalla internos.
- **Pruebas:** suites offline con la IA simulada en las dos aplicaciones (41 y 45 casos) más
  pruebas reales documentadas en [`docs/pruebas.md`](docs/pruebas.md).
- **Seguridad:** sin secretos en git (`.env` ignorado, `.env.example` ficticio), `/docs` cerrado
  en producción, cabeceras de seguridad, saneado anti-inyección de prompt (`formato.py`) y
  verificación de tokens de Clerk en el backend.
- **IA sin alucinaciones:** reglas en mensaje `system` (sin nombres propios de locales, todo
  dentro de la ciudad pedida), `temperature 0.2` y variación aleatoria por petición.
- **Accesibilidad y diseño:** responsive, foco de teclado, mensajes anunciados y maquetación
  comprobada hasta 320 px.
- **Alcance respetado:** cero persistencia, cero CRUD, cero pantallas adicionales.

## Metas de proceso y equipo

- **Dos procesos comparables:** App 1 manual e incremental; App 2 con Spec Kit
  (spec → plan → tareas → código, artefactos versionados antes del código).
- **Registro continuo:** cada cambio con su hito, autor y tiempo en
  [`docs/changelog.md`](docs/changelog.md); las decisiones en [`docs/proceso.md`](docs/proceso.md).
- **Identidad Git propia** de cada integrante y revisión cruzada en los PR.
- **IA como herramienta de apoyo:** el equipo entiende, ejecuta y justifica cada decisión
  (registro previsto en `docs/uso-ia.md`).
- **Documentación como entregable:** README (ES/EN), ERS, documento técnico, pruebas,
  comparativa y despliegues.

## Pendientes conocidos (estado honesto)

| Pendiente | Detalle | Dónde |
|---|---|---|
| `docs/uso-ia.md` | Registro del uso de la IA, exigido por el enunciado | [`docs/comparativa.md`](docs/comparativa.md) §5 |
| Comparativa de App 1 y errores | Completar tiempos, calidad, errores y mantenibilidad con evidencias | [`docs/comparativa.md`](docs/comparativa.md) |
| Captura del flujo completo de Clerk en producción | Google y cierre de sesión documentados con captura | [`docs/comparativa.md`](docs/comparativa.md) §Conclusión |
| Etiquetas de versión (`git tag`) | Las versiones de [`CHANGELOG.md`](CHANGELOG.md) aún no están marcadas con tags | [`CHANGELOG.md`](CHANGELOG.md) |

## Próximos pasos (H12 · cierre)

1. Completar [`docs/comparativa.md`](docs/comparativa.md) con las fases y errores de App 1.
2. Crear `docs/uso-ia.md` con el registro crítico del uso de la IA.
3. Cerrar la presentación de la defensa ([`presentacion/`](presentacion/)).
4. Publicar tags de versión coherentes con [`CHANGELOG.md`](CHANGELOG.md).

---

<div id="english-version"></div>

# Project Goals (English Version)

**[🇪🇸 Versión en español](#metas-del-proyecto--project-goals)**

> Goals of the **Itinerary Planner** project (PR01-UD1).
> The formal requirements baseline is [`docs/ERS.md`](docs/ERS.md); day-to-day work is in
> [`docs/proceso.md`](docs/proceso.md); changes and time tracking are in [`CHANGELOG.md`](CHANGELOG.md)
> and [`docs/changelog.md`](docs/changelog.md).

## Overall goal

Build, deploy, and document **two versions** of a **single-screen** web mini-app that returns a
one-day plan using **a single AI API**, following **two clearly distinguishable development
processes** (manual and incremental vs. specification-driven with GitHub Spec Kit + Clerk), with
tests, evidence, real deployments, and a defense before the instructor.

## Academic goals (PR01-UD1 deliverable)

| # | Goal | How it is measured | Status |
|---|---|---|---|
| M1 | Complete milestones H0–H12 | [`docs/changelog.md`](docs/changelog.md) (per-milestone log) | ✅ H0–H11 · 🔄 H12 (wrap-up) |
| M2 | Requirements spec traceable to the rubric | [`docs/ERS.md`](docs/ERS.md) v2.1 (OBJ, RF, RNF, Annex C) | ✅ |
| M3 | Compare both processes with evidence | [`docs/comparativa.md`](docs/comparativa.md) | 🔄 partial (App 1 phases and errors pending) |
| M4 | Critical log of AI usage | `docs/uso-ia.md` | ⬜ pending (not created yet) |
| M5 | Verifiable deployments | [`docs/despliegues.md`](docs/despliegues.md) + [README URLs](README.md#urls-despliegues) | ✅ Vercel (App 1 & App 2) · ✅ EC2 with Docker |
| M6 | Documented automated tests | [`docs/pruebas.md`](docs/pruebas.md) | ✅ App 1: 41 tests (17/10) · ✅ App 2: 45 tests (29/10) |
| M7 | Presentation and defense | [`presentacion/`](presentacion/) | 🔄 script and slides ready |

## Product goals (OBJ-01 … OBJ-05 from the SRS)

| ID | Goal | Achievement indicator |
|---|---|---|
| OBJ-01 | One useful function: input → one-day plan on the same screen | Without navigating to another view (CA-RF04-01) |
| OBJ-02 | Clear HTTP contract, errors without exposing internals | 200/422/502/504/500 (and 401 in App 2) tested |
| OBJ-03 | Simplicity: one screen, one AI API, zero persistence | No router, no database, no `localStorage` (RNF-02) |
| OBJ-04 | Two distinguishable development processes | H0–H7 (App 1) vs. Spec Kit artifacts before code (App 2) |
| OBJ-05 | Deployment and authentication as required | Vercel; App 2 also with Clerk and Docker on AWS EC2 |

## Quality goals

- **Contract:** server-side validation, `422`/`502`/`504`/`500` (and `401` in App 2) errors with
  `{"error":{"codigo","mensaje"}}`; no internal details ever leak.
- **Tests:** offline suites with a mocked AI in both applications (41 and 45 cases) plus real
  tests documented in [`docs/pruebas.md`](docs/pruebas.md).
- **Security:** no secrets in git (`.env` ignored, fictitious `.env.example`), `/docs` disabled
  in production, security headers, prompt-injection sanitizing (`formato.py`), and Clerk tokens
  verified in the backend.
- **Hallucination-free AI:** rules in a `system` message (no proper names of venues, everything
  inside the requested city), `temperature 0.2`, and random variation per request.
- **Accessibility and design:** responsive, keyboard focus, announced messages, and layout
  verified down to 320 px.
- **Scope respected:** zero persistence, zero CRUD, zero extra screens.

## Process and team goals

- **Two comparable processes:** App 1 manual and incremental; App 2 with Spec Kit
  (spec → plan → tasks → code, artifacts versioned before the code).
- **Continuous logging:** every change with its milestone, author, and time in
  [`docs/changelog.md`](docs/changelog.md); decisions in [`docs/proceso.md`](docs/proceso.md).
- **Individual Git identity** for each member and cross-review on pull requests.
- **AI as a support tool:** the team understands, runs, and justifies every decision
  (log planned in `docs/uso-ia.md`).
- **Documentation as a deliverable:** README (ES/EN), SRS, technical document, tests,
  comparison, and deployments.

## Known gaps (honest status)

| Gap | Detail | Where |
|---|---|---|
| `docs/uso-ia.md` | Critical AI-usage log required by the assignment | [`docs/comparativa.md`](docs/comparativa.md) §5 |
| App 1 comparison and errors | Finish times, quality, errors, and maintainability with evidence | [`docs/comparativa.md`](docs/comparativa.md) |
| Full Clerk flow capture in production | Google sign-in and sign-out documented with a screenshot | [`docs/comparativa.md`](docs/comparativa.md) §Conclusion |
| Version tags (`git tag`) | [`CHANGELOG.md`](CHANGELOG.md) versions are not tagged yet | [`CHANGELOG.md`](CHANGELOG.md) |

## Next steps (H12 · wrap-up)

1. Complete [`docs/comparativa.md`](docs/comparativa.md) with App 1 phases and errors.
2. Create `docs/uso-ia.md` with the critical AI-usage log.
3. Finish the defense presentation ([`presentacion/`](presentacion/)).
4. Publish version tags consistent with [`CHANGELOG.md`](CHANGELOG.md).
