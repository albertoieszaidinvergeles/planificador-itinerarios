# Tareas: Planificador diario de turismo

**Documentos de entrada**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contrato frontend](./contracts/frontend-integration.md), [quickstart.md](./quickstart.md).

**Alcance**: Solo `app2/frontend` y `docs/pruebas.md`. No modificar `app2/backend`, `app1` ni el despliegue H10.

**Regla de ejecución**: completar una tarea, revisar sus cambios y realizar la comprobación manual indicada antes de empezar la siguiente. Esperar la revisión humana tarea a tarea. No se incluyen tareas de tests automáticos.

## Formato

- Todas las tareas usan `- [ ] Tnnn [P?] [USn?] descripción`.
- `[P]` solo se usaría para trabajo que realmente pueda hacerse en paralelo; estas tareas se mantienen secuenciales por la revisión humana requerida.
- Las tareas de setup/fundacionales y polish no llevan etiqueta de historia. Todas las tareas de una fase de historia llevan `[US1]`, `[US2]` o `[US3]`.
- Cada tarea nombra el archivo exacto que modifica y termina con una comprobación que puede revisarse antes de avanzar.

## Fase 1: Setup — proyecto base

**Objetivo**: preparar el proyecto de frontend vacío con las dependencias autorizadas y el esqueleto Vite/Tailwind.

- [x] T001 Definir en `app2/frontend/package.json` una SPA privada con scripts `dev`, `build` y `preview`, Vue 3 y Clerk como dependencias, y solo Vite, `@vitejs/plugin-vue`, Tailwind CSS v4 y `@tailwindcss/vite` como dependencias de desarrollo; comprobación manual: verificar que aparecen exactamente los seis paquetes permitidos y ningún router, store, axios o herramienta de pruebas.
- [x] T002 Ejecutar `npm install` desde `app2/frontend` usando exclusivamente las dependencias de `app2/frontend/package.json` y generar `app2/frontend/package-lock.json`; comprobación manual: revisar que el lockfile corresponde al manifiesto y que `npm install` no se ejecutó desde otra carpeta ni instaló paquetes globales.
- [x] T003 Ajustar `app2/frontend/.env.example` para documentar solo `VITE_CLERK_PUBLISHABLE_KEY` y `VITE_API_BASE_URL`, con un ejemplo de URL local y comentario que indique que la base queda vacía en producción; comprobación manual: confirmar que no aparecen claves secretas ni variables adicionales.
- [x] T004 Configurar `app2/frontend/vite.config.js` con los plugins oficiales de Vue y Tailwind CSS v4; comprobación manual: verificar que importa `@vitejs/plugin-vue` y `@tailwindcss/vite`, y no incorpora plugins de pruebas, proxies ni servicios adicionales.
- [x] T005 Crear `app2/frontend/src/style.css` con la importación CSS oficial de Tailwind v4 y estilos base de legibilidad; comprobación manual: confirmar que usa `@import "tailwindcss";` y no depende de otra hoja/framework externo.
- [x] T006 Crear `app2/frontend/index.html` con metadatos en español y el elemento de montaje Vue; comprobación manual: confirmar que contiene un único punto de montaje y no define rutas ni vistas.

## Fase 2: Fundacional — Clerk y pantalla inicial

**Objetivo**: arrancar la SPA con Clerk y mostrar el armazón de la pantalla en la misma vista.

- [x] T007 Crear en `app2/frontend/src/App.vue` el armazón de la pantalla única con `SignInButton` en modo modal y `UserButton` para la sesión activa; comprobación manual: verificar en el template que el acceso no navega a una página propia y que la sesión activa expone el control de usuario.
- [x] T008 Crear `app2/frontend/src/main.js` para montar Vue, cargar `src/style.css` e instalar `clerkPlugin` con `VITE_CLERK_PUBLISHABLE_KEY`; comprobación manual: iniciar `npm run dev` desde `app2/frontend`, confirmar que se muestra el armazón de la pantalla y probar el modal y el control de sesión con una clave publicable de desarrollo.

## Fase 3: Historia de usuario 1 — completar y generar un plan (Prioridad: P1, MVP)

**Objetivo**: una persona autenticada completa los datos y recibe el plan diario en la pantalla única.

**Prueba independiente**: seguir en [quickstart.md](./quickstart.md) los casos de sesión, validación, compañía, petición/token, espera, plan completo y plan sin etiquetas completas. Comprobar el resultado manualmente antes de pasar a la historia siguiente.

### Formulario y validación

- [x] T009 [US1] Añadir a `app2/frontend/src/App.vue` los campos ciudad, fecha, personas y gustos con sus valores iniciales y etiquetas visibles; la ciudad debe aceptar de 1 a 80 caracteres, la fecha hoy o futura, personas un entero de 1 a 20 y gustos de 1 a 200 caracteres después de recortar los espacios exteriores (los espacios interiores cuentan, igual que en el backend); comprobación manual: verificar los cuatro controles y límites en la interfaz.
- [x] T010 [US1] Implementar en `app2/frontend/src/App.vue` la validación cliente de los cuatro campos, bloqueo de envío inválido y errores junto al campo correspondiente; comprobar literalmente: «ciudad de 1 a 80 caracteres», «fecha desde hoy», «personas un entero de 1 a 20» y «gustos de 1 a 200 caracteres»; comprobación manual: ejecutar los casos de validación de [quickstart.md](./quickstart.md) y confirmar que no se genera solicitud.
- [x] T011 [US1] Añadir en `app2/frontend/src/App.vue` el selector opcional de compañía: no mostrarlo con una persona, ofrecer Amigos y Familia con dos o más, ofrecer Pareja solo con exactamente dos y limpiar la opción si cambia el número de personas y deja de ser válida; comprobación manual: probar 1, 2 y más de 2 personas y el cambio posterior de selección.
- [x] T012 [US1] Incorporar en `app2/frontend/src/App.vue` al final de gustos el sufijo exacto «(van con amigos)», «(van en familia)» o «(van en pareja)», sin propiedad `compania` en el JSON; validar el total incluyendo gustos recortados, espacio separador y sufijo, con máximo 200 caracteres; comprobación manual: probar cada sufijo y los límites combinados de 200 y 201 caracteres sin exceder el contrato.

### Solicitud y espera

- [x] T013 [US1] Implementar en `app2/frontend/src/App.vue` el envío con `fetch` nativo al URL base más `/api/plan` o a `/api/plan` cuando la base esté vacía, solicitando a Clerk el token actual mediante `useAuth().getToken` justo antes de cada envío y enviando únicamente `ciudad`, `fecha`, `personas` y `gustos` con `Authorization: Bearer <token>`; si falta sesión o el token es `null`, no enviar y pedir iniciar sesión abriendo el modal de Clerk; comprobación manual: inspeccionar una solicitud válida y verificar cabecera, URL, cuerpo exacto y cero llamadas sin sesión.
- [x] T014 [US1] Implementar en `app2/frontend/src/App.vue` el estado de pantalla, con un único estado cada vez (entrada, espera, resultado o error), y el estado espera con indicador de carga, botón «Generar plan» deshabilitado y etiqueta «Generando…», bloqueando envíos repetidos; al iniciar un envío se borra el resultado anterior, sin historial; comprobar manualmente con una respuesta demorada que hay una sola petición, que la acción permanece bloqueada hasta recibir respuesta y que el resultado anterior desaparece al enviar de nuevo.

### Presentación del resultado

- [x] T015 [US1] Presentar en `app2/frontend/src/App.vue` el resultado válido como tarjetas Mañana, Tarde y Noche solo cuando las tres etiquetas estén presentes, y como texto completo si falta alguna; representar todo mediante interpolación Vue (`{{ }}`), nunca `v-html`, e incluir el aviso «Texto generado por IA, orientativo; comprueba sitios y horarios»; comprobación manual: probar ambos formatos y un texto que parezca HTML, verificando el aviso y que el marcado no se ejecuta.

## Fase 4: Historia de usuario 2 — comprender errores y recuperarse (Prioridad: P2)

**Objetivo**: la persona entiende errores del servicio y puede regresar al formulario conservando los datos, sin reenvíos automáticos.

**Prueba independiente**: seguir en [quickstart.md](./quickstart.md) los casos 422 conocido/desconocido, 401, 500/502/504, error de red y reintento; comprobar manualmente el número de solicitudes y los valores conservados.

- [x] T016 [US2] Manejar en `app2/frontend/src/App.vue` las respuestas 422 cuyo `detail` corresponda a ciudad, fecha, personas o gustos: la pantalla vuelve al estado entrada (no al estado error), mostrando el mensaje junto al campo conocido; si algún error no corresponde a un campo conocido, añadir un mensaje general; comprobación manual: verificar una respuesta con varias ubicaciones conocidas y otra ubicación desconocida.
- [x] T017 [US2] Manejar en `app2/frontend/src/App.vue` la respuesta 401 volviendo al estado entrada conservando los datos, con un mensaje general que pide iniciar sesión de nuevo (sin «Reintentar» ni reenvío automático), y las respuestas 500, 502 y 504 usando `error.codigo` y `error.mensaje` para mostrar un error comprensible; comprobar manualmente las cuatro respuestas y confirmar que el formulario se conserva.
- [x] T018 [US2] Manejar en `app2/frontend/src/App.vue` el fallo de red y las respuestas 200 sin `resultado` de texto utilizable con un mensaje recuperable, sin limpiar el formulario; comprobación manual: interrumpir la conexión y probar una respuesta 200 inesperada.
- [x] T019 [US2] Implementar en `app2/frontend/src/App.vue` la acción «Reintentar» para volver al estado de entrada conservando campos y compañía, sin obtener token ni emitir una solicitud hasta que se pulse «Generar plan»; comprobación manual: revisar la pestaña de red después de pulsar «Reintentar» y verificar cero nuevas peticiones.

## Fase 5: Historia de usuario 3 — accesibilidad y uso móvil (Prioridad: P3)

**Objetivo**: completar el flujo con teclado/tecnologías de asistencia y sin desbordamiento en móvil.

**Prueba independiente**: seguir en [quickstart.md](./quickstart.md) los casos de teclado, lector de pantalla y 320 px; verificar en la misma sesión de revisión los estados y asociaciones de error.

- [x] T020 [US3] Completar en `app2/frontend/src/App.vue` la asociación accesible de cada etiqueta, control y error mediante identificadores y atributos ARIA, anuncios de espera/resultado/error, y foco visible y operable por teclado; comprobación manual: recorrer el formulario y los estados con teclado y lector de pantalla y comprobar cada mensaje asociado.
- [x] T021 [US3] Ajustar `app2/frontend/src/style.css` y las clases de `app2/frontend/src/App.vue` para que formulario, selector, errores, controles y tarjetas funcionen a 320 px sin desplazamiento horizontal; comprobación manual: probar una ventana de 320 px y confirmar que todos los controles siguen utilizables.

## Fase 6: Pulido y verificación final

**Objetivo**: documentar el resultado de la verificación humana y comprobar que el bundle queda compilable y libre de secretos.

- [ ] T022 Añadir a `docs/pruebas.md` una sección de matriz manual «App 2 — Frontend» basada en los casos de [quickstart.md](./quickstart.md), con columnas para caso, resultado esperado, resultado observado, fecha y estado; comprobación manual: verificar que aparecen autenticación, validación, compañía, longitud combinada, solicitud, estados, errores, reintento, seguridad de texto, accesibilidad y móvil sin sobrescribir matrices existentes.
- [ ] T023 Ejecutar los casos manuales de [quickstart.md](./quickstart.md), `npm run build` desde `app2/frontend` e inspeccionar el bundle generado para detectar secretos; registrar en `docs/pruebas.md` la fecha, resultados observados, build y comprobación del bundle, sin copiar tokens ni valores secretos; comprobación manual: revisar la sección final y confirmar que cada caso tiene resultado y que no se divulgaron credenciales.
- [ ] T024 Revisión final del código y del navegador: buscar en `app2/frontend/src` `localStorage`, `sessionStorage`, `indexedDB` y `v-html` (cero resultados); en DevTools → Application, comprobar que la aplicación no guarda formulario ni resultado (las cookies o claves propias de Clerk se anotan como del SDK, no de nuestro código); comprobar que `main.js`, `App.vue` y `vite.config.js` tienen comentarios en español en inicialización, autenticación, validación, estados y solicitud; registrar el resultado en `docs/pruebas.md`.

## Dependencias y orden de ejecución

### Dependencias de fases

- **Setup (Fase 1)**: secuencial; cada tarea se revisa manualmente antes de la siguiente.
- **Fundacional (Fase 2)**: depende de completar setup; establece la pantalla inicial con Clerk y bloquea el trabajo de historias.
- **US1 (Fase 3)**: depende de setup y fundacional; sigue formulario → validación → compañía → petición → espera → resultado.
- **US2 (Fase 4)**: depende de US1 para integrar los errores y la recuperación con el formulario y la solicitud.
- **US3 (Fase 5)**: depende de US1 y US2, porque la accesibilidad y diseño deben abarcar todos los controles y estados.
- **Pulido (Fase 6)**: depende de las tres historias; se registran casos y se valida el build final.

### Grafo de historias

```text
Fase 1 Setup
    ↓
Fase 2 Fundacional: Vite + Tailwind + Clerk + pantalla visible
    ↓
US1 (P1): formulario → API/espera → resultado
    ↓
US2 (P2): errores → reintento sin envío automático
    ↓
US3 (P3): accesibilidad → móvil
    ↓
Fase 6: documentación → build y registro final
```

### Oportunidades de paralelismo

No se marcan tareas `[P]`: la revisión humana tarea a tarea y las sucesivas ediciones del mismo `App.vue` requieren ejecución secuencial. No hay trabajo independiente que justifique paralelismo sin saltarse ese control.

## Ejemplos de ejecución por historia

Las siguientes actividades son demostraciones manuales de los incrementos, no tareas adicionales:

- **US1**: después de T015, recorrer los casos de sesión, formulario, compañía, petición única, espera y formatos de resultado de [quickstart.md](./quickstart.md).
- **US2**: después de T019, provocar 422 conocido/desconocido, 401, 500/502/504, red fallida y reintento; comprobar valores retenidos y ausencia de envío automático.
- **US3**: después de T021, completar las verificaciones con teclado/lector de pantalla y en ventana de 320 px.

## Estrategia de implementación

### MVP

1. Completar T001–T008 para tener Vite, Tailwind y Clerk funcionando y mostrar la pantalla única.
2. Completar T009–T015 para validar datos y compañía, realizar la petición autenticada y mostrar el plan.
3. **Punto de revisión humana**: validar la historia US1 con sus casos de quickstart antes de iniciar US2.

### Entrega incremental

1. Setup y fundacional → proyecto funcional con sesión modal.
2. US1 → formulario válido y plan seguro en la misma pantalla.
3. US2 → todos los errores y recuperación explícita sin pérdida de datos.
4. US3 → accesibilidad y móvil.
5. Pulido → registrar verificación manual y `npm run build`.

## Resumen de conteo

- Setup: 6 tareas.
- Fundacional: 2 tareas.
- US1: 7 tareas.
- US2: 4 tareas.
- US3: 2 tareas.
- Pulido: 3 tareas.
- **Total**: 24 tareas; 0 tareas de tests automáticos.
