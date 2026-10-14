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
| 13/10/2026 | Incidencia | Primera llamada real a OpenRouter con `google/gemma-4-26b-a4b-it:free` y `google/gemma-4-31b-it:free`: ambas devuelven `429 Too Many Requests` | Causa: los dos Gemma gratuitos dependen solo de Google AI Studio, que estaba saturado; la cuenta no registró consumo (0/50 peticiones diarias). Se cambia de modelo. En H2, un 429 se traducirá a `502 IA_NO_DISPONIBLE` | Manuel |
| 13/10/2026 | Decisión | **Modelo de IA:** `nvidia/nemotron-3-super-120b-a12b:free` (proveedor Nvidia con disponibilidad del 100 % en ese momento; tamaño intermedio, propósito general). Reserva: `nvidia/nemotron-3.5-lightning:free`. Cierra **PEN-03** | Prueba real en `docs/pruebas.md`: plan en español legible, ~14 s | Manuel |
| 13/10/2026 | Decisión | **Forma de trabajar con IA en App 1:** Codigo escrito a mano, comprendido y ejecutado antes de seguir | Registro en `docs/uso-ia.md` | Manuel |
| 14/10/2026 | Decisión | **PEN-02 resuelta:** aceptada la idea del planificador de itinerarios simplificado (solo IA, sin APIs externas) | Respuesta del profesor; ERS §9 | Manuel |
| 14/10/2026 | Decisión | **PEN-07 resuelta:** no hace falta mostrar nada por terminal. Sin logging propio ni `print` de prompt, respuesta o clave; basta el access log de uvicorn, que no incluye contenido | prueba en `docs/pruebas.md` (14/10); ERS §9 | Manuel |
| 14/10/2026 | Decisión | Se desactiva el razonamiento del modelo (`"reasoning": {"enabled": false}`) en la llamada a OpenRouter: la respuesta baja de ~14 s a ~5 s. Se mantiene `AI_TIMEOUT=20` | Prueba en `docs/pruebas.md` (14/10) | Manuel |
| 15/10/2026 | Incidencia | Al probar el 502 con `AI_MODEL=...:free-xxx`, OpenRouter respondió normalmente: probablemente trata lo que va detrás de `:` como variante y lo tolera | Se probó con `modelo-que-no-existe` → `502 IA_NO_DISPONIBLE`. El nombre del modelo debe copiarse exacto | Manuel |

## Problemas abiertos

| Problema | Origen | Solución prevista | Estado |
|---|---|---|---|
| Respuesta de ~14 s con un timeout de 20 s: poco margen | Prueba real H1 | En H2, medir con el razonamiento del modelo desactivado; si no basta, subir `AI_TIMEOUT` y actualizar la ERS | Cerrado 14/10/2026: ~5 s con el razonamiento desactivado; se mantiene `AI_TIMEOUT=20` |
| Elegir modelo `:free` definitivo y comprobar su cuota | Fase backend (H1) | Probar con petición real manual y documentar en `docs/pruebas.md` | Cerrado 13/10/2026: `nvidia/nemotron-3-super-120b-a12b:free` (ver Registro) |
| Configurar CORS/Vercel para que frontend y backend se encuentren | Fase H7 | Dos proyectos de Vercel con `VITE_API_BASE_URL` y origen permitido | Abierto |
| | | | |

## Reglas del equipo

- Reparto y rotación de tareas; cada integrante con su identidad Git y contribuciones identificables.
- Todo cambio de alcance se refleja en la ERS (versión + historial) y en este registro.
- La IA asistente se usa para explicar y revisar; **el equipo entiende y justifica** cada decisión (registro en `docs/uso-ia.md`).
