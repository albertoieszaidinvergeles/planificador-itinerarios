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

// Instala Clerk antes de montar la única pantalla de la aplicación.
// proxyUrl: todas las llamadas al servidor de Clerk pasan por el proxy del
// mismo origen (/__clerk -> función api/clerk-proxy en Vercel), necesario
// porque la instancia production no tiene DNS propio (clerk.<app>.vercel.app).
createApp(App)
  .use(clerkPlugin, { publishableKey, proxyUrl: '/__clerk' })
  .mount('#app')
