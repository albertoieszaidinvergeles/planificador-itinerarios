# Validación manual: Planificador diario de turismo

Esta guía valida el frontend de App 2. No despliega la aplicación ni ejecuta pruebas automatizadas.

## Requisitos previos

- Node.js compatible con la versión de Vite instalada (la usada por App 1 requiere `^20.19.0` o `>=22.12.0`).
- Instancia de Clerk configurada para iniciar sesión con Google y la clave publicable correspondiente.
- Backend App 2 disponible en `http://127.0.0.1:8000` para la integración local.
- Navegador moderno con herramientas de desarrollo para inspeccionar solicitudes.

## Preparación

Desde PowerShell:

```powershell
Set-Location C:\Curso_Especializacion\Proyectos_Clase\DCS_Proyectos\planificador-itinerarios\app2\frontend
Copy-Item .env.example .env
npm install
```

Editar `.env` con únicamente estas variables:

```dotenv
VITE_CLERK_PUBLISHABLE_KEY=pk_test_<clave_publicable_del_entorno>
VITE_API_BASE_URL=http://127.0.0.1:8000
```

No copiar claves secretas ni tokens. Para producción, `VITE_API_BASE_URL` debe estar vacía; el despliegue no forma parte de este hito.

## Ejecución y comprobación de compilación

```powershell
npm run dev
```

Abrir la URL local de Vite indicada en la terminal y completar los casos manuales de abajo. Para validar que el bundle compila:

```powershell
npm run build
```

Resultado esperado: comando de build exitoso, sin instalar dependencias globales ni añadir un ejecutor de pruebas. Registrar casos y resultados en `docs/pruebas.md`.

## Casos manuales

| Caso | Acción | Resultado esperado |
|---|---|---|
| Inicio de sesión | Abrir el control de acceso y completar Google en el modal | Se permanece en la pantalla única; aparece el control de usuario con opción de cerrar sesión. |
| Sin sesión | Intentar generar un plan sin sesión activa | Se pide iniciar sesión; no se emite `POST /api/plan`. |
| Cierre de sesión | Cerrar sesión desde el control de usuario | Clerk termina la sesión; no se envían solicitudes sin una sesión válida. |
| Validación de campos | Probar ciudad vacía, más de 80 caracteres, fecha pasada, personas 0 y 21, gustos vacíos y gustos con más de 200 caracteres | Se impide la llamada y los errores aparecen junto a sus campos. Probar también límites válidos. |
| Compañía | Probar 1 persona, 2 personas y más de 2; cambiar el número después de elegir Pareja | El selector no se muestra con 1; Amigos/Familia con 2 o más; Pareja solo con exactamente 2; la selección se borra al quedar inválida. |
| Longitud combinada | Seleccionar compañía y ajustar gustos para que el sufijo y el separador hagan que el total llegue a 200 y lo supere por un carácter | 200 se acepta; más de 200 se rechaza junto al campo gustos sin enviar. |
| Token y solicitud | Con sesión y entrada válida, inspeccionar una solicitud en las herramientas de red | Una sola `POST /api/plan`, cabecera Bearer con token de sesión y JSON con solo ciudad, fecha, personas y gustos. No copiar ni guardar el token en la evidencia. |
| Espera y doble envío | Retrasar temporalmente la respuesta disponible en el entorno de prueba e intentar activar el envío más de una vez | Indicador de carga y «Generando…» visibles; botón deshabilitado; una sola solicitud. |
| Plan completo | Usar una respuesta `200` con las tres etiquetas | Tres tarjetas separadas y aviso de texto orientativo. |
| Plan sin etiquetas completas | Usar una respuesta `200` cuyo texto omite una o más etiquetas | Se muestra el resultado entero como texto, sin dividir. |
| Texto no confiable | Verificar un resultado que contenga texto con apariencia de HTML, como `<script>` | El contenido aparece literalmente y no se ejecuta. |
| Validación 422 | Verificar detalles ligados a campos conocidos y otro detalle con ubicación desconocida | Mensajes junto a campos identificados; aparece un mensaje general para el error no asociado. |
| Errores HTTP | Verificar respuestas 401, 500, 502 y 504 del contrato | 401 solicita nueva autenticación sin reenvío automático; errores 500/502/504 muestran mensaje comprensible y «Reintentar». |
| Reintento | En un error recuperable, pulsar «Reintentar» y observar la red | Vuelve al estado de entrada, mantiene todos los valores y no hay nueva solicitud hasta pulsar «Generar plan». |
| Error de red | Interrumpir el acceso al backend durante una solicitud | Mensaje genérico de red, formulario conservado y ninguna repetición automática. |
| CORS local de 401 | En desarrollo local, probar una sesión caducada o inválida si el navegador oculta el 401 por falta de CORS | Si `fetch` lo observa como fallo de red, se espera el mensaje genérico de red; no cambiar el backend para esta prueba. |
| Estado y accesibilidad | Recorrer entrada, espera, resultado y error con teclado y lector de pantalla | Estados distinguibles, foco visible, etiquetas y errores asociados, indicador de espera anunciado sin bloquear navegación. |
| Diseño móvil | Probar la pantalla a 320 px de ancho | Formulario, mensajes, acciones y resultado utilizables sin desplazamiento horizontal. |
| Estado transitorio | Completar el plan y recargar la página | No aparece historial ni se restauran formulario o resultado desde almacenamiento del navegador. |

## Exclusiones

- No ejecutar Vitest, Jest ni otra herramienta de pruebas añadida.
- No realizar pruebas contra servicios reales automatizadas.
- No desplegar ni configurar Vercel (`vercel.json`, `api/`); corresponde al hito H10.
- No modificar ni usar cambios de `app2/backend` o `app1` como parte de esta validación.
