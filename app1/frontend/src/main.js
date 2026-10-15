import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

// Punto de montaje: una sola app, sin router ni store (una pantalla no los necesita).
createApp(App).mount('#app')
