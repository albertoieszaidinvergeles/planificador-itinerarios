import { createApp } from 'vue'
import { clerkPlugin } from '@clerk/vue'
import App from './App.vue'
import './style.css'

// Obtiene la clave publicable de la configuración de Vite para el navegador.
const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

// Informa explícitamente si falta configurar Clerk en el entorno local.
if (!publishableKey) {
  throw new Error(
    'Falta VITE_CLERK_PUBLISHABLE_KEY. Configura la clave publicable de Clerk en app2/frontend/.env.',
  )
}

// Clerk tiene dos instancias:
//  - production (pk_live_…, Vercel): no tiene dominio propio, así que sus
//    llamadas pasan por el proxy del mismo origen /__clerk (proxy.js en Vercel;
//    en local, el proxy de vite.config.js con la clave secreta del backend).
//  - development (pk_test_…): funciona en cualquier dirección sin proxy ni
//    clave secreta, así que se conecta a Clerk directamente.
const usaProxyClerk = publishableKey.startsWith('pk_live_')

// Instala Clerk antes de montar la única pantalla de la aplicación.
createApp(App)
  .use(clerkPlugin, usaProxyClerk ? { publishableKey, proxyUrl: '/__clerk' } : { publishableKey })
  .mount('#app')
