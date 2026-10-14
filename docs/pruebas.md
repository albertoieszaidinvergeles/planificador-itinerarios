# Pruebas

## Cómo se ejecutan

```bash
cd app1/backend        # (App 2: cd app2/backend)
pytest -v
```

- La suite **nunca** consulta OpenRouter: `ia.py` se sustituye por un mock.
- Debe pasar **sin conexión a internet** y sin créditos disponibles.
- La prueba real de integración (abajo) se ejecuta a mano y se documenta aquí.

## Matriz de casos — App 1

| # | Caso | Entrada de prueba | Comprobación | Resultado |
|---|---|---|---|---|
| T01 | Entrada válida | Sevilla / 2026-10-10 / 2 / «museos y tapas» | `200`, cuerpo `{"resultado": ...}`, **una sola** llamada al mock | ⬜ |
| T02 | Entrada vacía o solo espacios | `gustos: "   "` | `422`, **cero** llamadas al mock | ⬜ |
| T03 | Límite de longitud (acepta) | `gustos` con 200 caracteres | `200` (o pasa la validación) | ⬜ |
| T04 | Límite superado (rechaza) | `gustos` con 201 caracteres | `422` y sin llamada a la IA | ⬜ |
| T05 | Fecha pasada | `fecha` anterior a hoy | `422` con detalle de campo | ⬜ |
| T06 | Personas fuera de rango | `personas: 0` y `personas: 21` | `422` en ambos | ⬜ |
| T07 | Fallo del proveedor | mock en modo excepción | `502 IA_NO_DISPONIBLE`, mensaje genérico, sin stack trace ni secretos | ⬜ |
| T08 | Timeout del proveedor | mock con demora > `AI_TIMEOUT` (20 s) | `504 IA_TIMEOUT` dentro del límite | ⬜ |
| T09 | Respuesta inesperada del proveedor | mock devuelve vacío o basura | Se trata como `502`; el contrato no se rompe | ⬜ |

## Matriz de casos — App 2 (además de los anteriores)

| # | Caso | Comprobación | Resultado |
|---|---|---|---|
| T10 | Sin cabecera `Authorization` | `401 NO_AUTENTICADO` y **cero** llamadas al mock de IA | ⬜ |
| T11 | Token firmado por otra clave / caducado | `401` (firma, emisor, caducidad y audiencia verificados; no basta decodificar) | ⬜ |
| T12 | Token válido | La petición continúa: validación de entrada y `200` en escenario normal | ⬜ |
| T13 | Acceso real con Google + cierre de sesión | Prueba manual documentada (captura sin secretos) | ⬜ |

## Prueba real de integración (manual, datos ficticios)

> Se ejecuta **fuera** de la suite rutinaria y se registra aquí con sus credenciales propias.

| Fecha | Comando / herramienta | Entorno | Respuesta (resumen) | Evidencia |
|---|---|---|---|---|
| 13/10/2026 | `python app1/backend/ia.py` (prueba directa de `consultar_ia`) con Sevilla / 2026-10-20 / 2 / «museos y tapas» | local, `google/gemma-4-26b-a4b-it:free` y `google/gemma-4-31b-it:free` | `429 Too Many Requests` en ambos: proveedor único (Google AI Studio) saturado; la cuenta no registró consumo (0/50 peticiones diarias) | Salida de terminal |
| 13/10/2026 | `python app1/backend/ia.py` con los mismos datos | local, `nvidia/nemotron-3-super-120b-a12b:free` | Plan de un día en español, texto legible; **~14 s** de respuesta (timeout configurado: 20 s) | Salida de terminal |
| 14/10/2026 | `uvicorn main:app --reload` y `POST /api/plan` desde `http://127.0.0.1:8000/docs` con Sevilla / 2026-10-20 / 2 / «museos y tapas»; repetida sin el campo `gustos` | local, `nvidia/nemotron-3-super-120b-a12b:free` | Caso válido: `200` con `{"resultado": "..."}` (~14 s). Sin `gustos`: `422` inmediato, sin llamada a la IA | Página `/docs` de FastAPI |
| 14/10/2026 | `POST /api/plan` desde `/docs` con Sevilla / 2026-10-20 / 2 / «museos y comida típica», tras desactivar el razonamiento del modelo (`"reasoning": {"enabled": false}`) | local, `nvidia/nemotron-3-super-120b-a12b:free` | `200` con el plan en **~5 s** (antes ~14 s). En la terminal solo aparece la línea del access log de uvicorn, sin prompt, respuesta ni clave | Página `/docs` y terminal |
| 15/10/2026 | `POST /api/plan` desde `/docs` con los límites de H2 | local, mismo modelo | Válido: `200`. `ciudad: "   "`, `fecha: "2020-01-01"` («La fecha no puede ser anterior a hoy.»), `personas: 0` y `21`, `gustos` > 200 caracteres: `422` inmediato, sin llamada a la IA. `AI_TIMEOUT=1`: `504 IA_TIMEOUT`. `AI_MODEL=modelo-que-no-existe`: `502 IA_NO_DISPONIBLE`; los dos con la forma `{"error": {"codigo", "mensaje"}}`. Nota: con `...:free-xxx` OpenRouter **no** dio error y respondió con el modelo normal | Página `/docs` |

## Comprobación de la interfaz (Fase D)

| # | Escenario | Esperado |
|---|---|---|
| I01 | Estado espera | Spinner visible y botón deshabilitado; doble clic no emite segunda petición |
| I02 | Error 422 | Mensaje junto al campo; formulario conserva los datos |
| I03 | Error 502/504 | Mensaje comprensible + reintento funcional |
| I04 | Dos envíos seguidos | Solo se ve el último resultado; nada queda tras recargar |
| I05 | `resultado` con `<script>` de prueba | Se muestra como texto, sin ejecutar |

## Reglas

1. Nunca probar frases exactas de un modelo real ni confundir «el endpoint responde» con validar errores.
2. Sin secretos en capturas ni en este archivo.
3. Ejecutar `pytest` antes de cada despliegue y anotar fecha y resultado.
