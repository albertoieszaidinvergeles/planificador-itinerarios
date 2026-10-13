# Proceso de desarrollo — decisiones e incidencias

Registro **cronológico** de decisiones del equipo y problemas con su solución. Se actualiza
cuando ocurren (no se rellena al final). Sin secretos, tokens ni respuestas de la IA
innecesarias.

## Registro

| Fecha | Tipo | Descripción | Resultado / verificación | Autor |
|---|---|---|---|---|
| 08/10/2026 | Decisión | **Idea:** «planificador de itinerarios» en versión **simplificada** (formulario → plan de un día como texto). Se retiran OpenStreetMap, mapa, validador de factibilidad, timeline estructurado y caché por la regla de simplicidad del enunciado (una sola función útil, una sola API de IA) | Documento técnico v3, §2; revisión de alcance con el docente → **PEN-02** | Equipo |
| 08/10/2026 | Decisión | Única API de IA = **OpenRouter** con modelo `:free`; la clave vive solo en backend (`AI_API_KEY`) | ERS R-12/RNF-02; `.env.example` | Equipo |
| 08/10/2026 | Decisión | Validación de campos en **FastAPI/Pydantic** (uvicorn solo sirve); contrato con códigos 200/422/502/504 y 401 en App 2 | Documento técnico §4 y §5.4 | Equipo |
| 08/10/2026 | Decisión | **Dos aplicaciones**: App 1 manual (Vercel) y App 2 desde cero con Spec Kit + Clerk (Vercel y Docker/EC2). ERS base común + Anexo C para Clerk | ERS leyenda de alcance y Anexo C | Equipo |
| 08/10/2026 | Decisión | Documentación en la raíz (README, ERS, documento técnico) y `docs/` para proceso/pruebas/comparativa/despliegues/uso-ia | README §Estructura | Equipo |
| 11/10/2026 | Decisión | La ERS se renombra a `docs/ERS.md` (lo exige el enunciado) y toda la documentación pasa a `docs/`. Sustituye a la decisión del 08/10 de tener la documentación en la raíz | PR #3; README §Estructura | Manuel |
| 13/10/2026 | Decisión | **Reparto de App 1:** Manuel se encarga del Backend (`main.py`, `ia.py`, tests) y Alberto del Frontend. Posiblemente en la App 2 se intercambian los papeles para que los dos conozcan todo el flujo | `docs/PropuestaFases.md`; PR de esta decisión revisada por Alberto | Manuel |
| | Incidencia | | | |

## Problemas abiertos

| Problema | Origen | Solución prevista | Estado |
|---|---|---|---|
| Elegir modelo `:free` definitivo y comprobar su cuota | Fase backend (H1) | Probar con petición real manual y documentar en `docs/pruebas.md` | Abierto (PEN-03) |
| Configurar CORS/Vercel para que frontend y backend se encuentren | Fase H7 | Dos proyectos de Vercel con `VITE_API_BASE_URL` y origen permitido | Abierto |
| | | | |

## Reglas del equipo

- Reparto y rotación de tareas; cada integrante con su identidad Git y contribuciones identificables.
- Todo cambio de alcance se refleja en la ERS (versión + historial) y en este registro.
- La IA asistente se usa para explicar y revisar; **el equipo entiende y justifica** cada decisión (registro en `docs/uso-ia.md`).
