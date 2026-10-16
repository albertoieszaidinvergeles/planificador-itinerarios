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

## Tiempo total por hito

| Hito | Manuel (min) | Alberto (min) | Total |
|---|---|---|---|
| H0 | 120 | 100 | 220 |
| H1 | 240 | | 240 |
| H2 | 60 | | 60 |
| H3 | 80 | | 80 |
| H4 | | 200 | 200 |
| H6 | | 130 | 130 |