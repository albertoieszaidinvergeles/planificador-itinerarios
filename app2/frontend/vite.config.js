import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const directorio = path.dirname(fileURLToPath(import.meta.url))

// Clave secreta de Clerk para el proxy local (solo la lee el servidor de
// desarrollo de Vite; nunca se incluye en el bundle del navegador).
function claveSecretaClerk() {
  try {
    const env = fs.readFileSync(
      path.join(directorio, '..', 'backend', '.env'),
      'utf8',
    )
    const coincidencia = env.match(/^CLERK_SECRET_KEY=(.+)$/m)
    return coincidencia ? coincidencia[1].trim() : ''
  } catch {
    return ''
  }
}

// Registra Vue y Tailwind CSS v4 en la compilación de Vite.
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    // En local, /__clerk/* se reenvía a la Frontend API de Clerk. Clerk no
    // acepta "http://localhost" como Clerk-Proxy-Url, así que se envía la URL
    // pública de producción (solo afecta a las URLs que genera Clerk).
    proxy: {
      '/__clerk': {
        target: 'https://frontend-api.clerk.dev',
        changeOrigin: true,
        rewrite: (ruta) => ruta.replace(/^\/__clerk/, ''),
        headers: {
          'Clerk-Proxy-Url': 'https://planificador-itinerarios.vercel.app/__clerk',
          'Clerk-Secret-Key': claveSecretaClerk(),
        },
      },
    },
  },
})
