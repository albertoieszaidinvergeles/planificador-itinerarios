# Modelo de datos: Planificador diario de turismo

Este modelo describe exclusivamente el estado transitorio del frontend App 2. El contrato de backend no cambia.

## Datos del formulario

| Atributo | Tipo conceptual | Reglas |
|---|---|---|
| `ciudad` | Texto | Obligatorio después de recortar espacios exteriores; de 1 a 80 caracteres. |
| `fecha` | Fecha ISO (`AAAA-MM-DD`) | Obligatoria; hoy o posterior según la fecha local de la persona. |
| `personas` | Entero | Obligatorio; de 1 a 20, inclusive. |
| `gustos` | Texto | Obligatorio después de recortar espacios exteriores; de 1 a 200 caracteres en el cuerpo enviado. |
| `compania` | Selección opcional (`amigos`, `familia`, `pareja`) | Estado solo del frontend, nunca propiedad del contrato. No se ofrece con una persona; Amigos y Familia se ofrecen con dos o más; Pareja solo con exactamente dos. Se limpia si el nuevo número de personas invalida la opción. |

### Normalización de la solicitud

- Se eliminan los espacios exteriores de ciudad y gustos antes de validar y enviar; los espacios interiores cuentan para el máximo.
- Si se elige compañía, se concatena al final de gustos un espacio y exactamente uno de estos sufijos: `(van con amigos)`, `(van en familia)` o `(van en pareja)`.
- Se valida el texto final enviado, incluidos el separador y el sufijo, contra el máximo de 200 caracteres.
- El JSON contiene exclusivamente `ciudad`, `fecha`, `personas` y `gustos`. No se añade el atributo `compania`.

## Sesión Clerk

Sesión temporal administrada por Clerk. El frontend solicita el token de sesión actual justo antes de cada envío autenticado y lo usa únicamente en la cabecera de esa petición. No mantiene una copia propia ni persiste tokens. La sesión puede cerrarse desde el control de usuario; ante un 401 se solicita volver a autenticarse y no se reenvía la petición.

## Estado de pantalla

La pantalla mantiene exactamente uno de estos estados de interacción:

| Estado | Contenido |
|---|---|
| `entrada` | Formulario, controles de sesión y acción «Generar plan». |
| `espera` | Formulario conservado, indicador de carga y «Generando…»; envío deshabilitado. |
| `resultado` | Resultado textual, en tres tramos solo si contiene las tres etiquetas reconocidas; aviso de contenido orientativo. |
| `error` | Mensaje apropiado a la causa (500, 502, 504, red o resultado inutilizable) y acción «Reintentar». |

Un 422 no lleva al estado `error`: la pantalla vuelve a `entrada` con los mensajes junto a los campos reconocidos y, si hay errores sin campo conocido, un mensaje general.

Un 401 tampoco: vuelve a `entrada` conservando los datos, con un mensaje general que pide iniciar sesión de nuevo, sin «Reintentar» ni reenvío automático.

Un error de generación, red o autenticación conserva los valores del formulario. La acción «Reintentar» vuelve a `entrada` sin petición; solo la acción explícita «Generar plan» inicia otra. Un nuevo envío elimina el resultado anterior. Una recarga descarta el estado del formulario y del resultado.

## Resultado y errores

- **Resultado**: texto recibido en `resultado`; es contenido no confiable y se presenta literalmente, nunca se interpreta como HTML.
- **Error de validación**: entradas de `detail`, opcionalmente asociadas a campos contractuales conocidos. Las ubicaciones desconocidas se comunican mediante un mensaje general.
- **Error de servicio**: `error.codigo` y `error.mensaje` en las respuestas 500, 502 o 504; el frontend comunica el fallo comprensiblemente y ofrece volver a entrada.
- **Sesión no autorizada**: 401; no se reintenta automáticamente.
- **Fallo de red**: mensaje genérico. En desarrollo local el navegador puede representar el 401 del backend como fallo de red debido a las cabeceras CORS conocidas.

## Conservación

Formulario, compañía, sesión accesible mediante Clerk, estado, errores y resultado existen solo mientras la pantalla está activa. El frontend no crea entidades persistentes, historial, almacenamiento de navegador, caché ni almacenamiento de resultados.
