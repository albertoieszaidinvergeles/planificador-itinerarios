import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// Configuración de Vite para la única pantalla de App 1.
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    port: 5173, // el backend permite este origen en CORS_ORIGINS
  },
})
