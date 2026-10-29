# Especificación de funcionalidad: Planificador diario de turismo

**Rama de funcionalidad**: No creada (no hay hook de rama configurado)

**Creada**: 2026-10-29

**Estado**: Borrador

**Entrada**: Planificador de un día de turismo para App 2. El alcance de esta especificación es exclusivamente `app2/frontend`; el backend existente de `001-backend-clerk-auth` no se modifica.

## Aclaraciones

### Sesión 2026-10-29

- Q: ¿Cómo se ofrece y se incluye la compañía del viaje en la planificación? → A: Selector opcional Amigos, Familia o Pareja; no aparece con una persona, Pareja solo está disponible con exactamente dos, y su sufijo se añade a gustos sin crear un campo del contrato ni superar 200 caracteres.
- Q: ¿Qué estados y acciones visibles debe tener la pantalla? → A: Entrada, espera con indicador de carga, resultado y error; el botón de envío se llama «Generar plan».
- Q: ¿Qué debe hacer la acción «Reintentar»? → A: Volver al estado de entrada conservando los datos del formulario, sin enviar automáticamente.
- Q: ¿Cómo se muestran los errores 422 que no corresponden a un campo conocido? → A: Mediante un mensaje general.

## Escenarios de usuario y pruebas

### Historia de usuario 1: Generar un plan turístico de un día (Prioridad: P1)

Una persona que quiere organizar una visita indica la ciudad, la fecha, cuántas personas viajarán y sus gustos; si viaja acompañada, puede indicar opcionalmente la compañía. Tras iniciar sesión, obtiene un plan organizado para la mañana, la tarde y la noche en la misma pantalla.

**Por qué tiene esta prioridad**: La generación del itinerario es el valor principal del producto y permite completar el objetivo de la aplicación.

**Prueba independiente**: Con una sesión válida y una respuesta correcta del servicio existente, completar el formulario y comprobar que se muestra un plan utilizable sin cambiar de pantalla.

**Escenarios de aceptación**:

1. **Dado** que no hay una sesión iniciada, **cuando** la persona intenta generar un plan, **entonces** se le pide iniciar sesión mediante una ventana modal en la pantalla actual y no se envía la solicitud.
2. **Dado** que la persona elige iniciar sesión con Google en la ventana modal, **cuando** la autenticación termina, **entonces** vuelve a la misma pantalla y ve el control de usuario que permite cerrar sesión.
3. **Dado** que hay una sesión válida y los cuatro campos contienen valores válidos, **cuando** la persona envía el formulario con «Generar plan», **entonces** se envía una única solicitud con los cuatro valores del contrato y la credencial de la sesión.
4. **Dado** que hay al menos dos personas, **cuando** se ofrece la compañía, **entonces** se puede elegir Amigos o Familia y Pareja solo está disponible si hay exactamente dos personas; con una persona no se muestra el selector.
5. **Dado** que se ha elegido una compañía, **cuando** se prepara la solicitud, **entonces** su sufijo se añade al final de gustos, sin enviar un campo nuevo y sin superar los 200 caracteres en total.
6. **Dado** que la generación está en curso, **cuando** se muestra el estado de espera, **entonces** la pantalla muestra un indicador de carga, el botón queda deshabilitado y muestra «Generando…», y no se admite un segundo envío.
7. **Dado** que la persona completa una solicitud correctamente, **cuando** cambia el estado de la pantalla, **entonces** se distinguen los estados de entrada, espera, resultado y error sin salir de la pantalla.
8. **Dado** que el servicio devuelve un plan correcto con las etiquetas Mañana, Tarde y Noche, **cuando** se presenta el resultado, **entonces** cada tramo aparece en su propia tarjeta y se muestra el aviso de que el texto fue generado por IA, es orientativo y se deben comprobar los sitios y horarios.
9. **Dado** que el texto de un plan contiene las tres etiquetas requeridas, **cuando** el contenido se presenta, **entonces** se muestra como texto literal y ningún marcado incluido se interpreta como contenido activo.

---

### Historia de usuario 2: Corregir datos y recuperarse de errores (Prioridad: P2)

La persona recibe indicaciones claras cuando faltan datos o el servicio no puede generar el itinerario, y puede volver al formulario sin perder lo que ya escribió ni provocar un reenvío automático.

**Por qué tiene esta prioridad**: Una validación comprensible y una recuperación sin pérdida evitan envíos inútiles y permiten completar la tarea cuando el servicio falla.

**Prueba independiente**: Probar límites y errores de validación, autenticación, servicio y red, verificando los mensajes, el número de solicitudes y la conservación del formulario.

**Escenarios de aceptación**:

1. **Dado** que un campo no cumple sus límites, **cuando** se intenta enviar, **entonces** el navegador impide la solicitud y muestra el error junto al campo correspondiente.
2. **Dado** que el servicio responde con errores de validación, **cuando** se recibe la respuesta, **entonces** cada error se muestra junto al campo al que corresponde.
3. **Dado** que el servicio responde que la sesión no está autenticada, **cuando** se recibe la respuesta, **entonces** se pide iniciar sesión de nuevo y no se reenvía el formulario automáticamente.
4. **Dado** que el servicio responde con un error de generación o se pierde la conexión, **cuando** se informa del problema, **entonces** se muestra un mensaje comprensible y la acción «Reintentar» vuelve al estado de entrada conservando los valores introducidos, sin volver a enviar.
5. **Dado** que se ha recibido un plan, **cuando** la persona inicia un nuevo envío, **entonces** el resultado anterior deja de mostrarse y el nuevo resultado se mantiene solo en memoria.
6. **Dado** que una respuesta 422 incluye un error sin campo conocido, **cuando** se muestra el error, **entonces** aparece un mensaje general además de los mensajes asociados a los campos que sí se reconozcan.

---

### Historia de usuario 3: Usar el planificador en móvil y con tecnologías de asistencia (Prioridad: P3)

La persona puede completar el formulario y comprender sus errores tanto en una pantalla móvil como usando navegación por teclado o tecnologías de asistencia.

**Por qué tiene esta prioridad**: El acceso a la planificación no debe depender del tamaño de pantalla ni de poder usar un ratón.

**Prueba independiente**: Completar y validar el formulario con una ventana de 320 píxeles de ancho y navegar por todos sus controles con teclado y lector de pantalla.

**Escenarios de aceptación**:

1. **Dado** que la pantalla tiene 320 píxeles de ancho, **cuando** se muestra el planificador, **entonces** los campos, el botón y las tarjetas pueden utilizarse sin desplazamiento horizontal.
2. **Dado** que una persona navega con teclado o lector de pantalla, **cuando** recorre el formulario y sus errores, **entonces** cada campo tiene una etiqueta accesible y cada mensaje de error queda asociado al campo correspondiente.

### Casos límite

- Los límites válidos son inclusivos: ciudad de 1 a 80 caracteres, fecha desde hoy, personas de 1 a 20 y gustos de 1 a 200 caracteres.
- Una ciudad o unos gustos formados únicamente por espacios se consideran vacíos; los espacios de los extremos no cuentan para los límites.
- Si se selecciona compañía, los gustos enviados incluyen al final «(van con amigos)», «(van en familia)» o «(van en pareja)», según corresponda; se cuenta el texto añadido y su separador dentro del máximo de 200 caracteres. Si el total lo supera, se impide el envío y se muestra el error junto a gustos.
- Si el número de personas cambia y la compañía seleccionada deja de ser válida, se borra esa selección; con una persona no se ofrece ninguna opción y con más de dos no se ofrece Pareja.
- Si el plan no contiene las tres etiquetas Mañana, Tarde y Noche, no se intenta dividirlo: se presenta el texto completo como una sola pieza.
- Si la respuesta de éxito no contiene un resultado utilizable, se informa del problema sin bloquear la pantalla y se permite reintentar conservando el formulario.
- Si la sesión caduca antes del envío o mientras se procesa, no se envían datos sin credencial válida y se solicita iniciar sesión otra vez.
- Una respuesta de red fallida no debe borrar el formulario ni producir envíos repetidos automáticos.
- La acción «Reintentar» solo vuelve a entrada y conserva también la compañía elegida; la persona debe pulsar «Generar plan» para realizar otra solicitud.
- Los errores 422 asociados a campos conocidos se muestran junto a esos campos; si `detail` contiene errores con ubicaciones desconocidas o sin campo, se añade un mensaje general.
- La pantalla distingue visualmente los estados entrada, espera, resultado y error; la espera incluye un indicador de carga.
- El resultado anterior se descarta al comenzar un nuevo envío; no se conserva un historial.
- El texto del plan puede incluir caracteres que parezcan etiquetas o marcado; siempre se muestra como texto sin interpretarlo.

## Requisitos

### Requisitos funcionales

- **RF-001**: La aplicación DEBE ofrecer una única pantalla, sin páginas propias de inicio de sesión ni navegación entre vistas.
- **RF-002**: La aplicación DEBE permitir iniciar sesión con Google mediante Clerk en una ventana modal dentro de la pantalla actual. Con una sesión iniciada, DEBE mostrar un control de usuario que permita cerrar sesión.
- **RF-003**: El formulario DEBE incluir ciudad, fecha, número de personas y gustos, con etiquetas visibles y accesibles. DEBE ofrecer, de forma opcional, un selector de compañía separado de los campos del contrato.
- **RF-004**: Tras quitar los espacios de los extremos, la ciudad DEBE tener de 1 a 80 caracteres y los gustos enviados de 1 a 200 caracteres (los espacios interiores sí cuentan, igual que en el backend); un texto formado solo por espacios se considera vacío. La fecha DEBE ser hoy o posterior y el número de personas DEBE ser un entero de 1 a 20, inclusive. Si se selecciona compañía, su sufijo y separador se incluyen en el límite total de gustos.
- **RF-005**: La aplicación DEBE validar los cuatro campos y el texto final de gustos antes de enviar. Si un valor no es válido, DEBE impedir la solicitud y mostrar el mensaje junto al campo correspondiente.
- **RF-006**: Si no hay una sesión válida, la aplicación DEBE pedir iniciar sesión y enviar cero solicitudes de planificación.
- **RF-007**: Cada envío válido y autenticado DEBE realizar exactamente una solicitud `POST /api/plan`, con ciudad, fecha, personas y gustos, y la cabecera `Authorization: Bearer <token de sesión de Clerk>`. La aplicación DEBE esperar a una acción explícita de la persona después de iniciar sesión; no enviará automáticamente el formulario.
- **RF-008**: La pantalla DEBE distinguir los estados de entrada, espera, resultado y error. El botón de envío DEBE llamarse «Generar plan». Mientras espera respuesta, la aplicación DEBE mostrar un indicador de carga y «Generando…», deshabilitar el botón e impedir cualquier segundo envío.
- **RF-009**: Ante una respuesta 200 con `resultado`, la aplicación DEBE separar el texto en tres tarjetas Mañana, Tarde y Noche solo si están presentes las tres etiquetas. Si falta alguna, DEBE mostrar el resultado completo sin dividirlo.
- **RF-010**: El plan y cualquier texto recibido DEBEN presentarse como texto, sin interpretar HTML ni otro marcado. Al presentar el plan, DEBE mostrarse el aviso: «Texto generado por IA, orientativo; comprueba sitios y horarios».
- **RF-011**: Ante una respuesta 422 con `detail`, la aplicación DEBE mostrar cada error cuyo campo se reconozca junto a ese campo y asociarlo accesiblemente; si uno o más errores no corresponden a un campo conocido, DEBE mostrar también un mensaje general.
- **RF-012**: Ante una respuesta 401, la aplicación DEBE pedir que la persona inicie sesión de nuevo y evitar un reenvío automático.
- **RF-013**: Ante una respuesta 500, 502 o 504 con `error.codigo` y `error.mensaje`, la aplicación DEBE mostrar un mensaje comprensible en el estado de error y ofrecer la acción «Reintentar».
- **RF-014**: Si falla la comunicación, la aplicación DEBE mostrar un mensaje genérico comprensible en el estado de error y ofrecer «Reintentar».
- **RF-015**: Ante una respuesta de éxito sin un `resultado` utilizable, la aplicación DEBE informar de que no pudo mostrar el plan en el estado de error y ofrecer «Reintentar».
- **RF-016**: El resultado DEBE permanecer únicamente en memoria hasta el siguiente envío. La aplicación DEBE mantener cero historial y cero persistencia de datos del formulario o del resultado en almacenamiento del navegador.
- **RF-017**: La aplicación DEBE limitar las comunicaciones a la autenticación de Clerk y al servicio existente de planificación; no añadirá otros servicios externos, rutas de navegación ni pantallas.
- **RF-018**: En móvil, el formulario y el resultado DEBEN poder utilizarse sin desplazamiento horizontal a partir de 320 píxeles de ancho. Los controles DEBEN ser operables con teclado y sus etiquetas y mensajes de error DEBEN estar asociados de forma accesible.
- **RF-019**: La compañía DEBE ser opcional; con una persona no se ofrecerá selector, con dos o más se ofrecerán Amigos y Familia, y Pareja solo se ofrecerá con exactamente dos personas. Si un cambio en el número de personas invalida la compañía elegida, la selección DEBE borrarse.
- **RF-020**: La compañía seleccionada DEBE añadirse al final de gustos como «(van con amigos)», «(van en familia)» o «(van en pareja)», según corresponda. No DEBE enviarse como un campo independiente. La suma de los gustos recortados, el separador y el sufijo DEBE respetar el máximo de 200 caracteres; si lo supera, se impedirá el envío y se mostrará el error junto a gustos.
- **RF-021**: La acción «Reintentar» DEBE volver al estado de entrada y conservar todos los datos del formulario, incluida la compañía seleccionada, sin realizar una solicitud. La persona deberá iniciar el siguiente envío mediante «Generar plan».

### Entidades clave

- **Datos de planificación**: ciudad, fecha, cantidad de personas y gustos; puede incluir una selección de compañía que se añade al final de gustos antes del envío y no constituye un campo separado del contrato.
- **Sesión autenticada**: sesión temporal de la persona, utilizada para autorizar el envío y acceder al control de usuario.
- **Plan diario**: texto recibido para un día de turismo, presentado como tres tramos cuando incluye las tres etiquetas requeridas o como texto completo en caso contrario.

## Criterios de éxito

### Resultados medibles

- **CE-001**: El 100 % de los valores fuera de los límites especificados se rechaza antes de enviar una solicitud, y los valores válidos en los límites se aceptan.
- **CE-002**: Cada envío válido con sesión produce exactamente una solicitud; un envío sin sesión o con datos inválidos produce cero solicitudes.
- **CE-003**: El 100 % de las respuestas de validación, sesión, servicio y red contempladas en esta especificación muestra el estado y la opción de recuperación correspondientes sin borrar el formulario.
- **CE-004**: En una pantalla de 320 píxeles de ancho, todos los campos, mensajes, controles y tarjetas son utilizables sin desplazamiento horizontal.
- **CE-005**: Las personas pueden completar la planificación desde una sola pantalla y navegar por todos los campos y acciones con teclado; los errores se anuncian junto al campo afectado.
- **CE-006**: El 100 % de las selecciones de compañía respeta las opciones permitidas por el número de personas, se integra en gustos sin añadir campos a la solicitud y se rechaza antes del envío si el total supera 200 caracteres.
- **CE-007**: En todos los errores con opción «Reintentar», esa acción vuelve al estado de entrada conservando formulario y compañía y produce cero solicitudes hasta que la persona elija «Generar plan».

## Supuestos

- La autenticación de Clerk con Google y el contrato del servicio `POST /api/plan` ya existen y están fuera del alcance de los cambios; esta funcionalidad solo consume esos servicios desde `app2/frontend`.
- El servicio devuelve errores 422 como `detail` y errores 500, 502 y 504 como `error.codigo` y `error.mensaje`, según el contrato existente.
- Para fechas se utiliza el día actual de la persona en su calendario local.
- Los sufijos de compañía se incorporan a gustos como indicaciones entre paréntesis, conservando el contrato existente.
- Tras volver a autenticarse o pulsar «Reintentar», la persona vuelve a iniciar el envío explícitamente; no se reutiliza el intento fallido automáticamente.
- La aplicación no persiste el formulario, el plan ni el historial; cualquier estado de sesión permanece bajo el control de Clerk.
- No se incluyen cambios de backend, historial, cuentas propias, varias pantallas ni integraciones distintas de Clerk y el servicio existente.
