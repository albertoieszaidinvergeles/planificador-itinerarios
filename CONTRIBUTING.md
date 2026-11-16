# Guía de contribución / Contributing Guide

**[🇬🇧 English version below](#contributing-guide)**

Gracias por querer contribuir al **Planificador de itinerarios** (PR01-UD1). Este repositorio es
un entregable de asignatura con **dos aplicaciones** y una **regla de alcance** estricta; lee estas
pautas antes de abrir un issue o un pull request.

*Thanks for contributing to the **Itinerary Planner** (PR01-UD1). This repository is a course
deliverable with **two applications** and a strict **scope rule**; please read these guidelines
before opening an issue or a pull request.*

---

## 1. Cómo empezar / Getting started

```bash
git clone https://github.com/albertoieszaidinvergeles/planificador-itinerarios.git
cd planificador-itinerarios
```

- **Prerrequisitos:** Python 3.10+, Node.js/npm y Git. La instalación completa está en el
  [`README.md`](README.md#instalación-y-ejecución).
- **Ramas:** crea una rama desde `main` con el prefijo y una descripción corta:
  - `feat/…` nueva funcionalidad · `fix/…` corrección · `docs/…` documentación
  - `test/…` pruebas · `refactor/…` refactorización · `chore/…` mantenimiento
- **Identidad Git:** cada integrante usa su propia identidad y sus contribuciones deben ser
  identificables en el historial.

## 2. Regla de alcance (importante) / Scope rule (important)

Una sola pantalla, un solo formulario, una sola función útil y **una sola API de IA** (OpenRouter).
**Cero persistencia** (sin BD, sin `localStorage`), sin CRUD y sin pantallas adicionales. Ver
[`docs/ERS.md`](docs/ERS.md).

Las propuestas que rompan esta regla (mapas, chat, historial, bases de datos, segunda pantalla…)
se cerrán con una explicación; no es que no nos gusten, es que el enunciado lo prohíbe.

*One screen, one form, one useful function, and **one AI API** (OpenRouter). **Zero persistence**
(no database, no `localStorage`), no CRUD, no extra screens. See [`docs/ERS.md`](docs/ERS.md).
Proposals breaking this rule (maps, chat, history, databases, a second screen…) will be closed with
an explanation: it is not a matter of taste, the assignment forbids them.*

## 3. Informar de un error / Reporting a bug

1. Busca si el error ya está reportado en [Issues](https://github.com/albertoieszaidinvergeles/planificador-itinerarios/issues).
2. Abre un issue con la **plantilla de error**, indicando: aplicación (App 1 / App 2), URL,
   pasos para reproducirlo, resultado esperado y entorno.
3. **Nunca incluyas secretos:** ni `AI_API_KEY`, ni `CLERK_SECRET_KEY`, ni valores reales de
   `.env`. Las claves publicables de Vercel/Clerk sí son públicas por diseño.

*Search existing [Issues](https://github.com/albertoieszaidinvergeles/planificador-itinerarios/issues)
first, then open one with the **bug report template** (app, URL, steps to reproduce, expected
result, environment). **Never include secrets:** no `AI_API_KEY`, no `CLERK_SECRET_KEY`, no real
`.env` values.*

## 4. Proponer un cambio / Proposing a change

1. Crea la rama `feat/…`, `fix/…` o `docs/…` desde `main`.
2. Haz el cambio **entendido y probado** por ti (si usas IA, el equipo debe poder explicarlo).
3. Ejecuta las pruebas de la aplicación afectada:
   - App 1: `cd app1\backend` → `pytest -v`
   - App 2: `cd app2\backend` → `.venv\Scripts\python.exe -m pytest -v`
4. Actualiza la documentación que el cambio afecte (README, ERS, `docs/pruebas.md`,
   `docs/despliegues.md`…).
5. Registra el cambio en [`docs/changelog.md`](docs/changelog.md) con **fecha, autor, hito
   (H0–H12), descripción y minutos**; las decisiones de fondo van en
   [`docs/proceso.md`](docs/proceso.md).
6. Abre un **pull request** con la plantilla rellena y pide revisión a otro integrante.

*Branch → change → run the tests → update the affected docs → log it in
[`docs/changelog.md`](docs/changelog.md) (date, author, milestone H0–H12, description, minutes) →
open a **pull request** using the template and request a review from another team member.*

## 5. Convenciones / Conventions

- **Commits:** mensaje en **español**, imperativo y concreto (`Añade validación de fecha`),
  referenciando el hito cuando aplique.
- **Idioma de los documentos:** los documentos principales son **bilingües** (español primero,
  inglés después), como el README.
- **Python:** sigue el estilo del módulo existente (FastAPI, validación en el contrato de
  errores, sin secretos en el código).
- **Vue:** sin router, sin `localStorage`, una sola pantalla; los estados son entrada, espera,
  resultado y error.
- **No subas nunca:** `.env` reales, claves, `__pycache__/`, `node_modules/` ni `dist/` fuera de
  lo ya versionado.

*Commit messages in **Spanish**, imperative and concrete; main documents are **bilingual**
(Spanish first, English after); follow the existing FastAPI/Vue style; never commit real `.env`
files, keys, `__pycache__/`, `node_modules/`, or stray `dist/` builds.*

## 6. Licencia / License

Al contribuir aceptas que tu aporte se publica bajo la licencia [`LICENSE`](LICENSE) del
proyecto (**MIT**).

*By contributing you agree that your contribution is published under the project's
[`LICENSE`](LICENSE) (**MIT**).*

## 7. Código de conducta / Code of conduct

Participar implica aceptar el [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Para reportar conducta
inaceptable o vulnerabilidades, sigue [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) y
[`SECURITY.md`](SECURITY.md): el contacto es **vía GitHub**, sin issues públicos si prefieres
canal privado.

*Participating means accepting the [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). To report
unacceptable behavior or vulnerabilities, follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
[`SECURITY.md`](SECURITY.md): contact is **via GitHub**, and you may ask for a private channel
instead of a public issue.*

---

<div id="contributing-guide"></div>

# Contributing Guide (English Version)

**[🇪🇸 Versión en español](#guía-de-contribución--contributing-guide)**

Thanks for wanting to contribute to the **Itinerary Planner** (PR01-UD1). This repository is a
course deliverable with **two applications** and a strict **scope rule**; read these guidelines
before opening an issue or a pull request.

## 1. Getting started

```bash
git clone https://github.com/albertoieszaidinvergeles/planificador-itinerarios.git
cd planificador-itinerarios
```

- **Prerequisites:** Python 3.10+, Node.js/npm, and Git. Full setup is in
  [`README.md`](README.md#installation--execution).
- **Branches:** branch from `main` with a prefix and a short description:
  - `feat/…` new feature · `fix/…` fix · `docs/…` documentation
  - `test/…` tests · `refactor/…` refactoring · `chore/…` maintenance
- **Git identity:** each member uses their own identity and contributions must be identifiable in
  the history.

## 2. Scope rule (important)

One screen, one form, one useful function, and **one AI API** (OpenRouter). **Zero persistence**
(no database, no `localStorage`), no CRUD, no extra screens. See [`docs/ERS.md`](docs/ERS.md).
Proposals breaking this rule (maps, chat, history, databases, a second screen…) will be closed with
an explanation: the assignment forbids them.

## 3. Reporting a bug

Search existing
[Issues](https://github.com/albertoieszaidinvergeles/planificador-itinerarios/issues) first, then
open one with the **bug report template** (app, URL, steps to reproduce, expected result,
environment). **Never include secrets:** no `AI_API_KEY`, no `CLERK_SECRET_KEY`, no real `.env`
values. Vercel/Clerk publishable keys are public by design.

## 4. Proposing a change

1. Create a `feat/…`, `fix/…`, or `docs/…` branch from `main`.
2. Make the change **understood and tested** by you (if you use AI, the team must be able to
   explain it).
3. Run the tests of the affected application:
   - App 1: `cd app1\backend` → `pytest -v`
   - App 2: `cd app2\backend` → `.venv\Scripts\python.exe -m pytest -v`
4. Update the documentation affected by the change (README, SRS, `docs/pruebas.md`,
   `docs/despliegues.md`…).
5. Log the change in [`docs/changelog.md`](docs/changelog.md) with **date, author, milestone
   (H0–H12), description, and minutes**; deeper decisions go to [`docs/proceso.md`](docs/proceso.md).
6. Open a **pull request** with the template filled in and request a review from another member.

## 5. Conventions

- **Commits:** message in **Spanish**, imperative and concrete (`Añade validación de fecha`),
  referencing the milestone when applicable.
- **Document language:** main documents are **bilingual** (Spanish first, English after), like the
  README.
- **Python:** follow the existing module style (FastAPI, contract-based errors, no secrets in
  code).
- **Vue:** no router, no `localStorage`, a single screen; states are input, waiting, result, and
  error.
- **Never commit:** real `.env` files, keys, `__pycache__/`, `node_modules/`, or stray `dist/`
  builds.

## 6. License

By contributing you agree that your contribution is published under the project's
[`LICENSE`](LICENSE) (**MIT**).

## 7. Code of conduct

Participating means accepting the [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). To report
unacceptable behavior or vulnerabilities, follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
[`SECURITY.md`](SECURITY.md): contact is **via GitHub**, and you may ask for a private channel
instead of a public issue.
