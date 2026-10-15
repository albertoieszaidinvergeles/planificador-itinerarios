<script setup>
/*
 * Versión funcional (H4 + estados): formulario con validación en cliente,
 * llamada a POST /api/plan y los cuatro estados de la pantalla única.
 * Estilo todavía básico: el diseño con Tailwind llega en el paso H6.
 */
import { reactive, ref } from 'vue'

// URL del backend: VITE_API_BASE_URL (pública) o la de desarrollo local.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

// Límites del contrato (idénticos a los de Pydantic en el backend).
const LIMITES = { ciudad: 80, gustos: 200, personasMin: 1, personasMax: 20 }

const estado = ref('entrada') // entrada | espera | resultado | error
const formulario = reactive({ ciudad: '', fecha: '', personas: 2, gustos: '' })
const erroresCampo = reactive({ ciudad: '', fecha: '', personas: '', gustos: '' })
const avisoGeneral = ref('')
const resultado = ref('')
const errorServidor = reactive({ codigo: '', mensaje: '' })

const fechaMin = hoyISO()

function hoyISO() {
  const hoy = new Date()
  const mes = String(hoy.getMonth() + 1).padStart(2, '0')
  const dia = String(hoy.getDate()).padStart(2, '0')
  return `${hoy.getFullYear()}-${mes}-${dia}`
}

function marcarCampo(campo, mensaje) {
  erroresCampo[campo] = mensaje
}

function limpiarErroresCampo() {
  for (const campo of Object.keys(erroresCampo)) erroresCampo[campo] = ''
}

function enfocarPrimerError() {
  const primerInvalido = document.querySelector('[aria-invalid="true"]')
  if (primerInvalido) primerInvalido.focus()
}

// La validación del cliente ayuda al usuario; NO sustituye a la del backend.
function validar() {
  limpiarErroresCampo()
  let correcto = true

  if (!formulario.ciudad.trim()) {
    marcarCampo('ciudad', 'Escribe la ciudad a la que vais.')
    correcto = false
  } else if (formulario.ciudad.trim().length > LIMITES.ciudad) {
    marcarCampo('ciudad', `Máximo ${LIMITES.ciudad} caracteres.`)
    correcto = false
  }

  if (!formulario.fecha) {
    marcarCampo('fecha', 'Elige la fecha del plan.')
    correcto = false
  } else if (formulario.fecha < fechaMin) {
    marcarCampo('fecha', 'La fecha no puede ser anterior a hoy.')
    correcto = false
  }

  const personas = Number(formulario.personas)
  if (!Number.isInteger(personas) || personas < LIMITES.personasMin || personas > LIMITES.personasMax) {
    marcarCampo('personas', `Entre ${LIMITES.personasMin} y ${LIMITES.personasMax} personas.`)
    correcto = false
  }

  if (!formulario.gustos.trim()) {
    marcarCampo('gustos', 'Cuéntanos qué os apetece (p. ej. «museos y tapas»).')
    correcto = false
  } else if (formulario.gustos.trim().length > LIMITES.gustos) {
    marcarCampo('gustos', `Máximo ${LIMITES.gustos} caracteres.`)
    correcto = false
  }

  return correcto
}

async function enviar() {
  // Sin envíos duplicados mientras hay una petición en curso.
  if (estado.value === 'espera') return

  avisoGeneral.value = ''
  errorServidor.codigo = ''
  errorServidor.mensaje = ''

  // Si algo no valida, no se hace NINGUNA llamada de red.
  if (!validar()) {
    estado.value = 'entrada'
    avisoGeneral.value = 'Revisa los campos marcados: no se ha enviado nada.'
    enfocarPrimerError()
    return
  }

  estado.value = 'espera'
  resultado.value = '' // un nuevo envío reemplaza al anterior

  try {
    const respuesta = await fetch(`${BASE_URL}/api/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ciudad: formulario.ciudad.trim(),
        fecha: formulario.fecha,
        personas: Number(formulario.personas),
        gustos: formulario.gustos.trim(),
      }),
    })

    const datos = await respuesta.json().catch(() => null)

    if (respuesta.ok) {
      if (datos && typeof datos.resultado === 'string' && datos.resultado.trim()) {
        resultado.value = datos.resultado.trim()
        estado.value = 'resultado'
      } else {
        mostrarError('RESPUESTA_INESPERADA', 'El servidor ha devuelto una respuesta inesperada. Inténtalo de nuevo.')
      }
      return
    }

    if (respuesta.status === 422) {
      manejar422(datos)
      return
    }

    // Errores controlados del contrato: 502 / 504 / 500…
    mostrarError(datos?.error?.codigo || 'ERROR_INTERNO', datos?.error?.mensaje || 'Error interno.')
  } catch {
    mostrarError('SIN_CONEXION', 'No se ha podido contactar con el servidor. Inténtalo más tarde.')
  }
}

function mostrarError(codigo, mensaje) {
  errorServidor.codigo = codigo
  errorServidor.mensaje = mensaje
  estado.value = 'error'
}

// Traduce el `detail` estándar de FastAPI/Pydantic a mensajes junto a cada campo.
function manejar422(datos) {
  const mensajes = {
    ciudad: `La ciudad es obligatoria (máximo ${LIMITES.ciudad} caracteres).`,
    fecha: 'Introduce una fecha válida de hoy en adelante (AAAA-MM-DD).',
    personas: `Debe haber entre ${LIMITES.personasMin} y ${LIMITES.personasMax} personas.`,
    gustos: `Los gustos son obligatorios (máximo ${LIMITES.gustos} caracteres).`,
  }

  limpiarErroresCampo()
  const detalle = Array.isArray(datos?.detail) ? datos.detail : []
  for (const item of detalle) {
    const campo = Array.isArray(item?.loc) ? item.loc[1] : null // loc = ["body", "campo"]
    if (campo && mensajes[campo] && !erroresCampo[campo]) marcarCampo(campo, mensajes[campo])
  }

  avisoGeneral.value = Object.values(erroresCampo).some(Boolean)
    ? 'El backend ha rechazado los datos (422): revisa los campos marcados. No se ha llamado a la IA.'
    : 'El backend ha devuelto 422: revisa los datos del formulario.'

  estado.value = 'entrada'
  enfocarPrimerError()
}

function reintentar() {
  estado.value = 'entrada'
  enviar()
}

function editarFormulario() {
  estado.value = 'entrada'
}

function nuevoPlan() {
  resultado.value = ''
  estado.value = 'entrada'
}

function cambiarPersonas(paso) {
  const actual = Number(formulario.personas) || LIMITES.personasMin
  formulario.personas = Math.min(LIMITES.personasMax, Math.max(LIMITES.personasMin, actual + paso))
}
</script>

<template>
  <main class="min-h-screen bg-zinc-950 px-4 py-10 text-zinc-100">
    <div class="mx-auto max-w-3xl">
      <h1 class="text-3xl font-bold">Planificador de itinerarios</h1>
      <p class="mt-2 text-zinc-400">Los cuatro campos son obligatorios.</p>

      <form
        class="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900 p-6"
        novalidate
        @submit.prevent="enviar"
      >
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label for="ciudad" class="block font-semibold">Ciudad</label>
            <input
              id="ciudad"
              v-model="formulario.ciudad"
              type="text"
              name="ciudad"
              :maxlength="LIMITES.ciudad"
              placeholder="Sevilla"
              class="mt-1.5 w-full rounded-lg border bg-zinc-950 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
              :class="erroresCampo.ciudad ? 'border-red-500' : 'border-zinc-700'"
              :aria-invalid="erroresCampo.ciudad ? 'true' : undefined"
              @input="erroresCampo.ciudad = ''"
            />
            <p v-if="erroresCampo.ciudad" class="mt-1 text-sm text-red-400">
              {{ erroresCampo.ciudad }}
            </p>
          </div>

          <div>
            <label for="fecha" class="block font-semibold">Fecha</label>
            <input
              id="fecha"
              v-model="formulario.fecha"
              type="date"
              name="fecha"
              :min="fechaMin"
              class="mt-1.5 w-full rounded-lg border bg-zinc-950 px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
              :class="erroresCampo.fecha ? 'border-red-500' : 'border-zinc-700'"
              :aria-invalid="erroresCampo.fecha ? 'true' : undefined"
              @input="erroresCampo.fecha = ''"
            />
            <p v-if="erroresCampo.fecha" class="mt-1 text-sm text-red-400">
              {{ erroresCampo.fecha }}
            </p>
          </div>

          <div>
            <label for="personas" class="block font-semibold">Personas</label>
            <div
              class="mt-1.5 flex items-center justify-between rounded-lg border px-2 py-1"
              :class="erroresCampo.personas ? 'border-red-500' : 'border-zinc-700'"
            >
              <button
                type="button"
                class="h-8 w-8 rounded-md bg-zinc-800 text-lg"
                aria-label="Quitar una persona"
                @click="cambiarPersonas(-1)"
              >
                −
              </button>
              <input
                id="personas"
                v-model.number="formulario.personas"
                type="number"
                name="personas"
                :min="LIMITES.personasMin"
                :max="LIMITES.personasMax"
                class="w-14 bg-transparent text-center focus:outline-none focus:ring-2 focus:ring-amber-500"
                :aria-invalid="erroresCampo.personas ? 'true' : undefined"
                @input="erroresCampo.personas = ''"
              />
              <button
                type="button"
                class="h-8 w-8 rounded-md bg-zinc-800 text-lg"
                aria-label="Añadir una persona"
                @click="cambiarPersonas(1)"
              >
                +
              </button>
            </div>
            <p v-if="erroresCampo.personas" class="mt-1 text-sm text-red-400">
              {{ erroresCampo.personas }}
            </p>
          </div>

          <div class="flex items-end">
            <p class="w-full rounded-lg border border-dashed border-zinc-700 px-3 py-2.5 text-sm text-zinc-400">
              Sin registro · sin cookies · sin base de datos
            </p>
          </div>

          <div class="sm:col-span-2">
            <div class="mb-1.5 flex items-center justify-between gap-3">
              <label for="gustos" class="block font-semibold">Gustos</label>
              <span class="text-sm text-zinc-500">{{ formulario.gustos.length }}/{{ LIMITES.gustos }}</span>
            </div>
            <textarea
              id="gustos"
              v-model="formulario.gustos"
              name="gustos"
              rows="3"
              :maxlength="LIMITES.gustos"
              placeholder="Museos, gastronomía y paseos…"
              class="w-full rounded-lg border bg-zinc-950 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
              :class="erroresCampo.gustos ? 'border-red-500' : 'border-zinc-700'"
              :aria-invalid="erroresCampo.gustos ? 'true' : undefined"
              @input="erroresCampo.gustos = ''"
            ></textarea>
            <p v-if="erroresCampo.gustos" class="mt-1 text-sm text-red-400">
              {{ erroresCampo.gustos }}
            </p>
          </div>
        </div>

        <button
          type="submit"
          class="mt-6 w-full rounded-lg bg-amber-500 px-5 py-3 font-bold text-zinc-950 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-zinc-900 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
          :disabled="estado === 'espera'"
          :aria-busy="estado === 'espera'"
        >
          {{ estado === 'espera' ? 'Generando…' : 'Generar plan' }}
        </button>
        <p class="mt-3 text-sm text-zinc-500">Tardará unos segundos · gratis · sin registro</p>
      </form>

      <!-- Zona de estados: solo uno visible -->
      <section class="mt-6" aria-live="polite">
        <div v-if="estado === 'entrada'">
          <div
            v-if="avisoGeneral"
            role="alert"
            class="rounded-xl border border-red-500 bg-red-950/40 p-4 text-sm text-red-300"
          >
            {{ avisoGeneral }}
          </div>
          <div v-else class="rounded-xl border border-dashed border-zinc-700 p-8 text-center text-zinc-400">
            <p class="font-semibold text-zinc-200">Aquí aparecerá tu plan</p>
            <p class="mt-1 text-sm">Rellena el formulario y pulsa «Generar plan».</p>
          </div>
        </div>

        <div
          v-else-if="estado === 'espera'"
          class="rounded-xl border border-zinc-800 bg-zinc-900 p-8 text-center"
        >
          <p class="font-semibold text-zinc-200">Generando tu plan…</p>
          <p class="mt-1 text-sm text-zinc-400">La IA tarda unos segundos. No cierres la página.</p>
        </div>

        <article v-else-if="estado === 'resultado'" class="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
          <div class="flex items-center justify-between gap-3">
            <h2 class="text-xl font-bold">Tu plan</h2>
            <button
              type="button"
              class="rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
              @click="nuevoPlan"
            >
              Nuevo plan
            </button>
          </div>

          <!-- Texto de la IA pintado como TEXTO ({{ }}), nunca con v-html -->
          <p class="mt-4 whitespace-pre-wrap leading-relaxed">{{ resultado }}</p>

          <p class="mt-5 rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-zinc-400">
            <strong class="text-amber-400">Aviso:</strong> texto generado por IA, orientativo y no
            verificado. Comprueba lugares, horarios y precios antes de salir.
          </p>
        </article>

        <div v-else role="alert" class="rounded-xl border border-red-500/50 bg-red-950/40 p-6 text-center">
          <h2 class="text-xl font-bold text-red-200">No hemos podido generar el plan</h2>
          <p class="mt-2 text-sm text-zinc-300">{{ errorServidor.mensaje }}</p>
          <p class="mt-3 inline-block rounded-full border border-red-500/50 px-3 py-1 font-mono text-sm text-red-300">
            {{ errorServidor.codigo }}
          </p>
          <div class="mt-5 flex flex-wrap justify-center gap-3">
            <button
              type="button"
              class="rounded-lg bg-amber-500 px-5 py-2.5 font-bold text-zinc-950 focus:outline-none focus:ring-2 focus:ring-amber-500"
              @click="reintentar"
            >
              Reintentar
            </button>
            <button
              type="button"
              class="rounded-lg border border-zinc-700 px-5 py-2.5 text-zinc-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
              @click="editarFormulario"
            >
              Editar el formulario
            </button>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>
