# Registro de cambios y tiempos

Registro de **qué se cambia** en el proyecto y **cuánto tiempo** se dedica. Se actualiza en
cada rama o PR, no al final. Los motivos de las decisiones van en [`proceso.md`](proceso.md).

- **Hito:** H0–H12 del enunciado (sirve para sumar el tiempo por fase en la comparativa).
- **Tiempo:** minutos de trabajo reales de esa persona en ese cambio.

## Registro

| Fecha | Autor | Hito | App | Cambio | Tiempo (min) | Rama / PR |
|---|---|---|---|---|---|---|
| 08/10/2026 | Equipo | H0 | Ambas | Documento técnico v3 y ERS v2.0 | | |
| 11/10/2026 | Manuel | H0 | Ambas | Revisión de la ERS: renombrada a `docs/ERS.md`, criterios de aceptación nuevos, trazabilidad y enlaces del README | 100 | PR #3 |
| 11/10/2026 | Alberto | H0 | Ambas | Versiones Markdown de `PropuestaFases` y `ResumenEnunciado` | | commit `2f1781a` |
| 13/10/2026 | Manuel | H0 | Ambas | Creación de este registro y reparto de App 1 en `proceso.md` | 20 | `docs/changelog-y-reparto` |
| 13/10/2026 | Manuel | H1 | App 1 | Entorno virtual, `requirements.txt`, `.env.example` e `ia.py` (primera llamada real a OpenRouter); elección del modelo | 180 | `feat/backend-minimo` |
| 14/10/2026 | Manuel | H1 | App 1 | `main.py` con `POST /api/plan` (llamada a la IA y respuesta según el contrato); pruebas en `/docs`; registro en `uso-ia.md` | 60 | `feat/backend-minimo` |
| 14-15/10/2026 | Manuel | H2 | App 1 | `ia.py` con errores propios (`IAError`, `IATimeout`) y razonamiento desactivado; `main.py` con límites de entrada, errores 502/504/500 según el contrato y CORS desde `CORS_ORIGINS`; pruebas manuales y documentación | 60 | `feat/contrato-errores` |
| 15/10/2026 | Alberto | H4 | App 1 | Base del frontend: `package.json`, `package-lock.json`, `index.html`, `vite.config.js`, `.env.example`, `src/main.js` y `src/style.css` (Vue 3 + Vite + Tailwind v4) | | `feat/frontend-formulario` |
| 15/10/2026 | Alberto | H4 | App 1 | Formulario único con validación en cliente, llamada a `POST /api/plan` y los cuatro estados de la pantalla única (entrada, espera, resultado, error) | | `feat/frontend-formulario` |
| 15/10/2026 | Alberto | H6 | App 1 | Diseño: tema oscuro de Figma con acento ámbar + modo claro conmutable en memoria, responsive, foco de teclado, resumen lateral y aviso de IA generado | | `feat/frontend-formulario` |
| 15/10/2026 | Alberto | H6 | App 1 | Chips «¿Con quién vais?» con reglas por número de personas, resultado en tarjetas Mañana/Tarde/Noche y limpieza del recuento de palabras que añade el modelo | | `feat/frontend-formulario` |
| 15-16/10/2026 | Manuel | H3 | App 1 | Tests con pytest y la IA simulada: `tests/test_plan.py` (T01–T09 y 500, 17 casos), `pytest.ini` y `requirements-dev.txt`; documentación en `pruebas.md` | 80 | `test/pytest-backend` |
| 16/10/2026 | Manuel | H5 | App 1 | Prompt de `ia.py` con formato fijo `Mañana:`/`Tarde:`/`Noche:` para las tarjetas del frontend (sin introducción ni recuento de palabras); test T09c; pruebas reales y documentación | 40 | `fix/prompt-etiquetas` |
| 16/10/2026 | Manuel | H2 | App 1 | Arreglos de seguridad del backend: `/docs` solo con `DOCS_ACTIVOS=1`, cabeceras de seguridad (middleware) y `--no-server-header`; test T09d; documentación | 30 | `fix/seguridad-backend` |
| 16/10/2026 | Manuel | H0 | Ambas | ERS v2.1: puesta al día con lo implementado (500, formato del prompt, compañía, Figma, RNF-02, PEN-08) y trazabilidad enlazada con `pruebas.md`; `Figma/` movido a `docs/evidencias/figma/` | 30 | `docs/ers-v2.1` |
| 17/10/2026 | Alberto | H2 | App 1 | Mitigación del hallazgo S18 (inyección de prompt): módulo nuevo `app1/backend/formato.py` (saneado de `ciudad`/`gustos` antes del prompt y comprobación del formato de la respuesta), **solo adiciones** en `ia.py` sin tocar el prompt, tests T09e/T09f en `tests/test_formato.py` y documentación en `pruebas.md` | 90 | `fix/s18-inyeccion-prompt` (PR #12) |
| 19/10/2026 | Alberto | H7 | App 1 | Despliegue en Vercel: proyecto único con raíz `app1/` (front + API en el mismo origen), `requirements.txt` aplanado porque el parser no resuelve `-r`, favicon SVG; regla de rate limit en el **WAF** (10/min en `/api/plan` → `429`); verificación en producción (**S19** cabeceras/contrato y **S21** rate limit) y documentación | | `984187f`, `224bf5c`, `e0dd063`, `3069210` |
| 19/10/2026 | Alberto | H4 | App 1 | Vercel Web Analytics en el frontend: `@vercel/analytics` con `inject()` en `main.js` solo en producción. El componente `<Analytics />` de `@vercel/analytics/vue` se descartó porque importa `useRoute` de `vue-router` (prohibido en esta app) | | `65d965a` |
| 19-20/10/2026 | Alberto | H5 | App 1 | **IA sin alucinaciones**: reglas en mensaje `system` (sin nombres propios de locales, describir «tipo + zona», sin datos no verificables, ciudad obligatoria, formato exacto), `temperature 0.2`, y variación por petición con `ENFOQUES` + `TOQUES` aleatorios y `seed` (dos peticiones idénticas ya no dan el mismo plan). Sin memoria ni estado | | `6420774`, `d4a6ca0`, `aa244cb` |
| 20/10/2026 | Alberto | H5 | App 1 | Pruebas de la IA en producción (6 peticiones reales a `/api/plan`, todas `200`) y documentación en `pruebas.md` §«Pruebas de la IA en producción» | | rama `main` |
| 22/10/2026 | Alberto y Manuel | H3 | App 2 | Añadido Spec Kit y reparados dos test tras el despliegue | | rama `main` |
| 29/10/2026 | Alberto | H8 | App 2 | Constitución de Spec Kit y especificación del backend con Clerk; plan, tareas, modelo de datos, quickstart y contrato API. Se fija que el `422` conserva el `detail` estándar de FastAPI de App 1 | 30 | `7258314`, `480d558`, `71c2c40`, `5e5fff0` |
| 29/10/2026 | Alberto | H9 | App 2 | Entorno y dependencias del backend (runtime separado de pytest), verificación Bearer/JWKS RS256, `POST /api/plan`, errores 401/422/502/504/500, CORS, cabeceras, docs condicionales, saneado/formato IA y suite offline | 120 | `6e82dd5`, `912574c`, `9c6d034` |
| 29/10/2026 | Alberto | H5 | Ambas | Actualizado `.env.example` para usar `nvidia/nemotron-3.5-lightning:free`; pruebas reales 5/5 documentadas. La variable `AI_MODEL` en Vercel continúa pendiente | 20 | `9c6d034` |

## Tiempo total por hito

| Hito | Manuel (min) | Alberto (min) | Total |
|---|---|---|---|
| H0 | 150 | 100 | 250 |
| H1 | 240 | | 240 |
| H2 | 90 | | 180 |
| H3 | 80 | 90 | 170 |
| H4 | | 200 | 200 |
| H5 | 40 | 20 | 60 |
| H6 | | 130 | 130 |
| H8 | | 30 | 30 |
| H9 | | 120 | 120 |