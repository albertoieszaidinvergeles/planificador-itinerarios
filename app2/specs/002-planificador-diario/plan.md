# Plan de implementación: Planificador diario de turismo

**Rama**: `main` (rama activa; el identificador de funcionalidad es `002-planificador-diario`) | **Fecha**: 2026-10-29 | **Especificación**: [spec.md](./spec.md)

**Entrada**: Plan técnico del frontend de App 2; exclusivamente `app2/frontend`.

## Resumen

Construir la aplicación de una sola pantalla de App 2 a partir de Vue 3, Vite y Tailwind CSS v4. La pantalla coordinará el inicio de sesión modal de Clerk, la validación del formulario y de la compañía opcional, la petición autenticada a `POST /api/plan` mediante `fetch`, y la presentación en texto seguro de estados, errores y resultado. Todo estado propio de la aplicación permanecerá en memoria. El contrato existente del backend no se modifica.

La implementación mantendrá el conjunto mínimo de dependencias indicado por el usuario, documentará pruebas manuales en `docs/pruebas.md` y no añadirá frameworks de prueba, rutas, almacenes, APIs adicionales ni trabajo de despliegue. La única limitación conocida es que, en desarrollo local, el backend no añade CORS a su respuesta 401: el navegador puede informar ese caso como fallo de red, que se mostrará con el mensaje genérico previsto.

## Contexto técnico

**Lenguaje/versión**: JavaScript con módulos ES; Vue 3. Vite 8 requiere Node.js `^20.19.0` o `>=22.12.0`, según el lockfile de App 1.

**Dependencias principales**: Dependencias de ejecución: `vue` y `@clerk/vue`. Dependencias de desarrollo: `vite`, `@vitejs/plugin-vue`, `tailwindcss` y `@tailwindcss/vite`. No se añadirán otras sin justificación explícita. No usar `vue-router`, Pinia ni axios. Clerk se inicializará mediante `clerkPlugin`; el control de acceso usará el botón oficial en modo modal y el control de usuario oficial.

**Almacenamiento**: Ninguno para los datos de la funcionalidad. Formulario, compañía, errores, estado de pantalla y resultado viven en estado reactivo en memoria; no se usan `localStorage`, `sessionStorage`, IndexedDB ni cachés propias.

**Pruebas**: Comprobación manual de interfaz e integración, registrada en `docs/pruebas.md`, más `npm run build`. No instalar Vitest ni otros ejecutores o herramientas de prueba.

**Plataforma destino**: Navegadores modernos de escritorio y móvil; interfaz usable desde 320 px de ancho, con teclado y tecnologías de asistencia.

**Tipo de proyecto**: SPA de frontend con una pantalla, sin router ni vistas navegables.

**Objetivos de rendimiento**: Una solicitud por envío válido; ninguna solicitud en caso de formulario inválido, ausencia de sesión o mientras otra solicitud está en curso. El estado de espera permanece hasta completar la respuesta del servicio, cuyo backend tiene su propio límite de tiempo.

**Restricciones**:

- Mantener intactos `app2/backend`, `app1` y el contrato documentado en `specs/001-backend-clerk-auth/contracts/plan-api.md`.
- El único envío de planificación es `POST /api/plan`, con los cuatro campos del contrato y `Authorization: Bearer <token de sesión Clerk>`.
- Solicitar el token vigente a Clerk justo antes de cada envío; no copiarlo ni persistirlo.
- Las únicas variables públicas de entorno son `VITE_CLERK_PUBLISHABLE_KEY` y `VITE_API_BASE_URL`. No incorporar claves secretas al frontend ni a su bundle. En producción `VITE_API_BASE_URL` queda vacía y se usa `/api/plan` en el mismo origen.
- En local se permite apuntar `VITE_API_BASE_URL` al backend de desarrollo; si una respuesta 401 carece de CORS y el navegador la presenta como fallo de red, se usa el mensaje genérico de red de la especificación, sin cambiar el backend.
- Mostrar el plan mediante interpolación de texto de Vue; nunca usar `v-html`.
- Dependencias instaladas únicamente desde `app2/frontend`; no instalar paquetes globales.
- El código tendrá comentarios en español que expliquen qué hace cada parte relevante, especialmente inicialización, autenticación, validación, estados y solicitud.
- El despliegue Vercel, incluidos `vercel.json` y `api/`, queda fuera del hito de este plan (H10).

**Alcance**: Una pantalla de planificación turística; inicio/cierre de sesión Clerk; formulario con ciudad, fecha, personas, gustos y compañía opcional incorporada al texto final de gustos; estados entrada/espera/resultado/error; errores recuperables; diseño móvil y accesibilidad; pruebas manuales documentadas.

## Comprobación de la constitución

| Principio | Comprobación antes del diseño |
|---|---|
| I. El contrato no se toca | La SPA consume el contrato existente y solo envía `ciudad`, `fecha`, `personas` y `gustos`; la compañía se incorpora a `gustos`, sin cambiar el modelo ni las respuestas del backend. |
| II. Cero secretos | Se utiliza solo la clave publicable de Clerk en el navegador; `CLERK_SECRET_KEY` y cualquier clave de IA no forman parte del frontend ni del bundle. |
| III. Identidad externa | Clerk provee inicio de sesión con Google en modal y el token de sesión para cada petición; no se añaden usuarios propios. La verificación sigue siendo responsabilidad del backend existente. |
| IV. Pruebas primero y sin conexión | No se cambia ni se añade ninguna prueba de backend. Para el frontend se respeta el requisito específico de pruebas manuales documentadas, sin incorporar herramientas de test ni llamadas reales en CI. |
| V. Entorno limpio | Los paquetes se declaran e instalan dentro de `app2/frontend`, limitados a la lista indicada. No se incorporan herramientas ni servicios adicionales. |
| VI. Una sola pantalla y estado en memoria | No se crea router, store, historial ni persistencia en navegador. El estado de UI y el resultado se conservan solo en memoria. |

**Resultado de la puerta previa**: Aprobada. No se detectan desviaciones de la constitución.

## Diseño técnico

### Organización propuesta

La carpeta `app2/frontend` contiene actualmente `.env.example`; se completará como proyecto Vue/Vite sin alterar el backend ni la App 1.

- `app2/frontend/package.json` y `package-lock.json`: scripts de desarrollo y compilación y dependencias permitidas.
- `app2/frontend/index.html`: documento anfitrión de la SPA.
- `app2/frontend/vite.config.js`: plugins oficiales de Vue y Tailwind CSS v4.
- `app2/frontend/src/main.js`: inicialización de Vue y configuración del SDK de Clerk con la publishable key.
- `app2/frontend/src/App.vue`: pantalla única, formulario, selector opcional de compañía, sesión, estados, validación, llamada API y presentación segura del plan.
- `app2/frontend/src/style.css`: importación de Tailwind v4 y estilos de enfoque/ajustes que requiera la accesibilidad.
- `app2/frontend/.env.example`: documenta solo `VITE_CLERK_PUBLISHABLE_KEY` y `VITE_API_BASE_URL`; dirección local para desarrollo y valor vacío para producción.
- `docs/pruebas.md`: nuevos casos manuales de aceptación del frontend App 2, sin sustituir ni reescribir las matrices ya existentes.

**Decisión de estructura**: Mantener un componente principal para la única pantalla y no añadir capas o componentes separados hasta que aporten una necesidad real. Clerk se inicializa con `clerkPlugin` en el punto de entrada; la pantalla utiliza el botón oficial `SignInButton` en modo modal y `UserButton` para la sesión activa. El formulario y sus transiciones se mantienen en el componente de pantalla.

### Flujo de solicitud y estados

1. En entrada, validar ciudad, fecha, personas y gustos, además de la compañía elegida y el límite de longitud del texto final de gustos.
2. Si falta sesión, abrir el acceso modal de Clerk sin emitir la petición. Con sesión, obtener el token vigente mediante la función devuelta por `useAuth().getToken` inmediatamente antes de iniciar la petición. Si Clerk devuelve `null`, no enviar nada y solicitar autenticación.
3. Mientras espera, mostrar indicador de carga y «Generando…», deshabilitar el botón «Generar plan» y bloquear cualquier envío duplicado.
4. Enviar una sola petición al URL base configurado más `/api/plan`, normalizando las barras finales; cuando la base esté vacía, resolver a `/api/plan`. Adjuntar únicamente los cuatro campos del contrato y la cabecera de autorización.
5. Convertir éxito, error controlado y fallo de red a los estados de resultado o error especificados. Un 422 se asocia a campos conocidos y presenta un aviso general si quedan errores sin campo reconocido; un 401 solicita autenticación de nuevo. Los fallos de comunicación muestran el mensaje genérico.
6. La acción «Reintentar» vuelve a entrada, conserva todos los valores y no solicita un token ni realiza otra petición; el siguiente envío requiere pulsar «Generar plan».
7. El resultado se limpia al iniciar un envío nuevo y se representa como texto. Solo se divide en tres tarjetas si están presentes las tres etiquetas del formato; si no, se conserva íntegro.

### Compañía y validación

- Con una persona no se muestra el selector. Con dos o más personas se ofrecen Amigos y Familia; Pareja solo se ofrece con exactamente dos.
- Si cambia el número de personas y la elección vigente deja de ser válida, se limpia la compañía.
- Al enviar, la selección se incorpora a gustos con el sufijo definido en [data-model.md](./data-model.md); no se añade una propiedad al cuerpo JSON.
- Se valida el valor final de gustos, incluido el espacio separador y sufijo: máximo 200 caracteres. Si lo supera, no hay solicitud y se muestra el error en gustos.
- Las restricciones se validan en cliente antes de obtener token o acceder a la red, manteniendo el backend como autoridad final del contrato.

## Contratos e interfaces

El contrato de backend permanece inalterado; la SPA implementa el subconjunto de solicitud y respuesta descrito en [contracts/frontend-integration.md](./contracts/frontend-integration.md), que referencia el contrato existente de App 2. La integración con Clerk sigue la guía oficial para Vue, incluida la naturaleza nullable del token de sesión, detallada en [research.md](./research.md).

El contrato visual define una sola pantalla con cuatro estados distinguibles, formulario etiquetado, selector de compañía dependiente de personas, autenticación modal de Clerk, botón de usuario y cierre de sesión, presentación de resultado como texto, errores asociados y recuperación accesible.

## Plan de validación

Seguir [quickstart.md](./quickstart.md) y añadir los resultados manuales a `docs/pruebas.md`. Cubrir autenticación y cierre de sesión, validación de límites, compañía y longitud combinada, ausencia de envíos sin sesión, petición única y cabecera, prevención de doble envío, respuestas 200/422/401/500/502/504, error de red, reintento sin reenvío, formato de resultado, seguridad de texto, teclado, lector de pantalla y 320 px. Ejecutar `npm run build` en la carpeta `app2/frontend`.

La prueba local del 401 debe registrar la limitación conocida de CORS: si el navegador oculta esa respuesta y la comunica como error de red, el resultado esperado del frontend es el mensaje genérico de red. No corregirlo desde el frontend ni cambiar el backend dentro de este alcance.

## Comprobación de la constitución tras el diseño

| Principio | Comprobación posterior |
|---|---|
| I. Contrato | El documento de interfaz no introduce cambios en el backend ni campos adicionales en el JSON; se conserva el endpoint y los estados/cuerpos existentes. |
| II. Secretos | Solo la publishable key aparece entre las variables frontend; verificar el bundle compilado para asegurar que no contiene claves secretas. |
| III. Clerk | El navegador obtiene y adjunta el token actual; la autorización real sigue dependiendo de la verificación del backend. |
| IV. Pruebas | La validación queda en escenarios manuales documentados y compilación; no hay nuevas dependencias de testing. |
| V. Dependencias | Solo los seis paquetes aprobados; lockfile y node_modules pertenecen a `app2/frontend`. |
| VI. Estado y UX | Una sola pantalla, transiciones en memoria, sin router/store/almacenamiento/cachés; salida textual segura. |

**Resultado de la puerta posterior**: Aprobada. H10 y cualquier modificación a `app2/backend` o `app1` están explícitamente fuera del plan.

## Seguimiento de complejidad

No hay desviaciones que justificar. No se añade infraestructura, una capa de estado global ni herramientas de prueba.
