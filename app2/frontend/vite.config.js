import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// Registra Vue y Tailwind CSS v4 en la compilación de Vite.
export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
