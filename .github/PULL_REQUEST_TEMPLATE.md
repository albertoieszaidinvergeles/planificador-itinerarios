<!-- Plantilla de pull request / Pull request template — rellena ambas columnas / fill in both columns. -->

## Descripción / Description

<!-- ¿Qué cambia y por qué? · What changes and why? -->

-

## Relación con los hitos / Milestone

<!-- H0–H12 · ver docs/changelog.md -->

- Hito / Milestone:

## Tipo de cambio / Type of change

- [ ] `feat/` funcionalidad nueva · new feature
- [ ] `fix/` corrección · bug fix
- [ ] `docs/` documentación · documentation
- [ ] `test/` pruebas · tests
- [ ] `refactor/` mejoras internas sin cambiar comportamiento · internal improvement, no behaviour change
- [ ] `chore/` mantenimiento · maintenance

## Checklist

- [ ] He ejecutado las pruebas de la aplicación afectada y pasan:
  - App 1: `cd app1\backend` → `pytest -v` (41 tests)
  - App 2: `cd app2\backend` → `python -m pytest -v` (47 tests)
- [ ] No he subido secretos (`.env`, `AI_API_KEY`, `CLERK_SECRET_KEY`, claves reales).
- [ ] He actualizado la documentación afectada (README, ERS, `docs/…`).
- [ ] He registrado el cambio en `docs/changelog.md` (fecha, autor, hito, cambio, minutos).
- [ ] He registrado las decisiones en `docs/proceso.md`, si las hay.
- [ ] Si cambia el alcance, he actualizado `docs/ERS.md` (versión + historial).
- [ ] El cambio respeta la regla de alcance: una pantalla, una API de IA, cero persistencia.

- [ ] I ran the tests of the affected application and they pass (App 1: 41, App 2: 47).
- [ ] I did not upload secrets (`.env`, `AI_API_KEY`, `CLERK_SECRET_KEY`, real keys).
- [ ] I updated the affected documentation (README, SRS, `docs/…`).
- [ ] I logged the change in `docs/changelog.md` (date, author, milestone, change, minutes).
- [ ] I logged decisions in `docs/proceso.md`, if any.
- [ ] If the scope changed, I updated `docs/ERS.md` (version + history).
- [ ] The change respects the scope rule: one screen, one AI API, zero persistence.

## Revisión / Review

- [ ] Otro integrante ha revisado el PR · Another member has reviewed this PR
- [ ] CI en verde (tests + build de frontends + enlaces de documentación) · CI green
