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
| 15/10/2026 | Decisión | **El Figma se usa solo como referencia visual**, no como estructura: estaba redactado con varias pantallas y mapa, y el enunciado pide **una sola pantalla** sin servicios externos | Fondo oscuro + acento ámbar aplicados; se añade **modo claro** conmutable por el usuario, **sin persistir** (R-03: nada de `localStorage`) | Alberto |
| 15/10/2026 | Decisión | La UI **no muestra nada académico** (sin «PR01-UD1», «App 1», autores ni nombres de proveedor), ni en la interfaz ni en el `<title>`/meta description | Revisión de `index.html` y `src/App.vue`; pensado para producción | Alberto |
| 15/10/2026 | Decisión | La **compañía** (amigos/familia/pareja) **no es un campo nuevo del contrato**: se envía dentro de `gustos` (p. ej. «museos y tapas (van con amigos)»), validando la longitud combinada ≤ 200 | `POST /api/plan` intacto; reglas: **1 persona → las tres opciones desactivadas**, **>2 personas → «Pareja» desactivada**, **2 → las tres activas**, con icono y borde discontinuo (no solo texto) | Alberto |
| 15/10/2026 | Decisión | El titular «hora a hora» no correspondía a lo que pide el prompt (mañana/tarde/noche): se cambia el copy a **«de la mañana a la noche»** | Frontend, sin tocar `ia.py` | Alberto |
| 15/10/2026 | Incidencia | El modelo añadía **«(248 palabras)»** al final de la respuesta porque el prompt pide «menos de 250 palabras» | Se quita ese trozo final en el frontend (`limpiarTexto()` en `App.vue`); el prompt de `ia.py` se deja como está | Alberto |
| 15/10/2026 | Decisión | El resultado se pinta en **tres tarjetas Mañana/Tarde/Noche** partir el texto de la IA por esas etiquetas; si no aparecen, se muestra el texto tal cual | Sigue siendo texto literal con `{{ }}` (nunca `v-html`), CA-RF04-03 | Alberto |
| 15/10/2026 | Verificación | Prueba de la API con payloads inválidos (201 caracteres, array, fecha pasada, 999, JSON vacío/malformado, `personas: "dos"` y extras tipo `admin`/`__proto__`/`sql`) | Todos **`422` sin llamar a la IA**; el envío válido con extras devuelve `200` con **solo** la clave `resultado`. Sin secretos en el bundle (`dist`) | Alberto |
| 15/10/2026 | Verificación | **Batería de pruebas de seguridad** contra el propio proyecto desde una VM **Kali Linux** en VirtualBox (ffuf, nikto, sqlmap, wafw00f, commix, nuclei y pruebas a medida con `curl`), con el backend expuesto en `0.0.0.0` **solo durante la prueba** | Resultados en `docs/pruebas.md` §«Pruebas de seguridad (App 1)»: sin inyección SQL, ni XSS, ni fugas de secretos, ni ficheros ocultos. Hallazgos abiertos: `/docs` y `/openapi.json` públicos, sin rate limit, sin límite de tamaño y cabeceras de seguridad ausentes | Alberto |
| 15/10/2026 | Incidencia | Durante esa batería **caducó la clave de prueba de OpenRouter**: todas las llamadas legítimas devolvían `502 IA_NO_DISPONIBLE` en <1 s, imitando un fallo del proveedor | Causa real: clave caducada en `.env` (no del modelo ni de la red). Se renovó el `.env`, se reinició uvicorn (lee la clave al arrancar) y las pruebas se repitieron con éxito. Los 73 `502` que generó sqlmap se explican igual: **no se gastó cuota** | Alberto |
| 16/10/2026 | Decisión | **Formato fijo en el prompt** de `ia.py`: tres líneas que empiezan por `Mañana:`, `Tarde:` y `Noche:` (cada etiqueta una sola vez), actividades en la misma línea separadas por `;` y empezando con mayúscula, sin introducción ni despedida y sin indicar el número de palabras. Motivo: el frontend parte el texto por esas etiquetas para pintar tres tarjetas | Test `test_prompt_pide_las_etiquetas_del_frontend` (T09c) vigila que el prompt siga pidiendo las etiquetas; pruebas reales en `docs/pruebas.md` (16/10) | Manuel |
| 16/10/2026 | Incidencia | Con el primer ejemplo de formato («Mañana: dos o tres actividades»), la IA repitió la etiqueta en **cada actividad**: 9 tarjetas en vez de 3, y con la primera letra en minúscula | La IA copia el ejemplo al pie de la letra: se pide «cada etiqueta UNA sola vez», las actividades en la misma línea separadas por `;` y un ejemplo que empieza con mayúscula. Tras el cambio, varias pruebas con exactamente 3 tarjetas correctas | Manuel |

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
