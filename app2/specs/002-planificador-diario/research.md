# Investigación: Planificador diario de turismo

## Decisiones técnicas

### Integración de Clerk en Vue 3

- **Decisión**: Inicializar el SDK oficial `@clerk/vue` con `clerkPlugin` y `VITE_CLERK_PUBLISHABLE_KEY`; usar `SignInButton` en modo modal y `UserButton` para la cuenta y el cierre de sesión; obtener el token actual mediante `await getToken.value()` justo antes de `fetch`.
- **Racional**: La guía oficial de Clerk documenta el SDK para Vue 3/Vite, el plugin de contexto, el modo modal, el control de usuario y la obtención del token de sesión antes de una llamada autenticada. `getToken` es una referencia de Vue a una función asíncrona; su resultado puede ser `null`, por lo que la solicitud solo debe continuar si existe token.
- **Alternativas consideradas**: Rutas propias de login, autenticación implementada manualmente o transportar la clave secreta al navegador. Se descartan por el requisito de modal en pantalla única, uso exclusivo del SDK oficial y prohibición de secretos en frontend.
- **Compatibilidad consultada**: Los metadatos de `@clerk/vue` versión 2.5.16 declaran Vue `^3.2.0` y Node `>=20.9.0` como peer/engine respectivamente. El manifiesto de dependencias y el lockfile fijarán la versión resuelta en el frontend, sin agregar paquetes auxiliares.
- **Referencias oficiales**:
  - [Clerk Vue quickstart](https://clerk.com/docs/vue/getting-started/quickstart.md?manual=1)
  - [Clerk Vue plugin](https://clerk.com/docs/vue/reference/clerk-plugin.md)
  - [Clerk Vue SignInButton](https://clerk.com/docs/vue/reference/components/unstyled/sign-in-button.md)
  - [Clerk Vue UserButton](https://clerk.com/docs/vue/reference/components/user/user-button.md)
  - [Clerk Vue SignOutButton](https://clerk.com/docs/vue/reference/components/unstyled/sign-out-button.md)
  - [Clerk Vue useAuth](https://clerk.com/docs/vue/reference/composables/use-auth.md)
  - [Metadatos npm de @clerk/vue](https://registry.npmjs.org/%40clerk%2Fvue/latest)

### Tailwind CSS v4 y Vite

- **Decisión**: Usar `tailwindcss` junto con `@tailwindcss/vite`, registrar el plugin oficial en `vite.config.js` e importar Tailwind desde la hoja CSS de la aplicación.
- **Racional**: Es el flujo recomendado por Tailwind para Vite v4 y coincide con el plugin de la aplicación App 1. El plugin declara las dependencias de ejecución de Tailwind; no se añadirá PostCSS/configuración auxiliar si el flujo oficial no la requiere.
- **Alternativas consideradas**: Tailwind v3 con configuración PostCSS, CDN o estilos de framework adicional. Se descartan porque el requisito fija v4, limita las dependencias y requiere integrar los estilos en la compilación Vite.
- **Referencias oficiales**:
  - [Instalación de Tailwind CSS v4 con Vite](https://tailwindcss.com/docs/installation/using-vite)
  - [Metadatos npm de @tailwindcss/vite](https://registry.npmjs.org/%40tailwindcss%2Fvite/latest)
  - [Metadatos npm de tailwindcss](https://registry.npmjs.org/tailwindcss/latest)

### Entorno Vite y dependencias

- **Decisión**: Mantener Node.js `^20.19.0` o `>=22.12.0` como entorno soportado por Vite 8, y declarar solo las seis dependencias explícitamente aprobadas por el usuario. Instalar y generar lockfile desde `app2/frontend`.
- **Racional**: El lockfile existente de App 1 usa Vite 8 y documenta esos límites de Node; los metadatos oficiales de Vite consultados confirman el requisito para la versión vigente. `@clerk/vue` es la única dependencia funcional adicional autorizada.
- **Alternativas consideradas**: Vite anterior o instalar dependencias globalmente. Se descartan para mantenerse con el stack del proyecto y las restricciones del entorno.
- **Referencias**:
  - [Metadatos npm de Vite](https://registry.npmjs.org/vite/latest)
  - `app1/frontend/package-lock.json` (referencia local del rango Node usado por Vite 8).

### Pruebas y limitación CORS local

- **Decisión**: Validación del frontend mediante escenarios manuales documentados en `docs/pruebas.md` y compilación `npm run build`; no añadir Vitest u otro ejecutor. No cambiar el comportamiento de CORS del backend dentro de este plan.
- **Racional**: La constitución y la petición excluyen herramientas de test adicionales y excluyen cambios de backend. El frontend debe aplicar el mensaje genérico de red cuando el navegador no puede exponer el 401 por la configuración local CORS existente.
- **Alternativas consideradas**: Proxy Vite para simular una respuesta accesible, modificación del middleware CORS o automatización con nuevo framework de pruebas. Se descartan porque amplían el alcance o contradicen las restricciones expresas.
- **Referencia**: Constitución de App 2, principios IV y V; contrato existente en `specs/001-backend-clerk-auth/contracts/plan-api.md`.

## Incógnitas

No quedan decisiones técnicas abiertas que bloqueen el plan. La versión concreta de cada paquete se resolverá al crear el manifiesto/lockfile dentro de `app2/frontend`, respetando los rangos de compatibilidad y la lista cerrada de dependencias.
