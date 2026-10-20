import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { inject } from '@vercel/analytics'

// Punto de montaje: una sola app, sin router ni store (una pantalla no los necesita).
createApp(App).mount('#app')

// Analítica de Vercel (Web Analytics): solo en producción. No usa cookies ni
// localStorage ni cuenta nada dentro de la app (el enunciado prohíbe cachés y
// contadores): son métricas de página que se ven en el panel de Vercel. El
// script se sirve del propio dominio (/_vercel/insights/…), así que también lo
// admite la CSP del vercel.json.
if (import.meta.env.PROD) {
  inject({ mode: 'production' })
}
