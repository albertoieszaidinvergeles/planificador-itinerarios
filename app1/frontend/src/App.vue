<script setup>
/*
 * LA ÚNICA PANTALLA de App 1 (R-01): formulario + resultado.
 * Sin router, sin store y sin persistencia: el resultado vive en memoria
 * hasta el siguiente envío o hasta que se recarga la página (R-03).
 *
 * Estados (solo uno visible a la vez):
 *   entrada  → formulario listo
 *   espera   → spinner y botón deshabilitado (impide envíos duplicados)
 *   resultado→ texto del plan
 *   error    → mensaje controlado del backend + reintento
 */
import { computed, reactive, ref, watch } from 'vue'

/* ------------------------------------------------------------------ *
 * Configuración
 * ------------------------------------------------------------------ */

// URL del backend. En Vercel (producción) se deja VITE_API_BASE_URL vacío para
// llamar a /api/plan en el mismo origen: sin CORS y sin cambiar nada al volver
// a desplegar. En local, si no se define, se usa el backend de desarrollo.
const BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
).replace(/\/+$/, '')

// Límites del contrato (idénticos a los de Pydantic en el backend).
const LIMITES = { ciudad: 80, gustos: 200, personasMin: 1, personasMax: 20 }

/*
 * Compañía con la que se hace el plan. NO es un campo del contrato: se añade
 * al final de `gustos` antes de enviar, así el backend y la IA lo reciben
 * sin cambiar POST /api/plan.
 * Reglas: con 1 persona no se ofrece; «Pareja» solo vale con exactamente 2.
 */
const OPCIONES_COMPANIA = [
  { valor: 'amigos', texto: 'Amigos', sufijo: '(van con amigos)' },
  { valor: 'familia', texto: 'Familia', sufijo: '(van en familia)' },
  { valor: 'pareja', texto: 'Pareja', sufijo: '(van en pareja)' },
]

/* ------------------------------------------------------------------ *
 * Estado de la pantalla
 * ------------------------------------------------------------------ */

const estado = ref('entrada') // entrada | espera | resultado | error
const formulario = reactive({ ciudad: '', fecha: '', personas: 2, gustos: '' })
const erroresCampo = reactive({ ciudad: '', fecha: '', personas: '', gustos: '' })
const avisoGeneral = ref('') // avisos en estado entrada (p. ej. validación 422)
const resultado = ref('') // texto devuelto por el backend (texto plano, nunca HTML)
const errorServidor = reactive({ codigo: '', mensaje: '' })
const temaOscuro = ref(true) // el boceto del Figma es oscuro; se puede cambiar a claro
const compania = ref('') // '' | amigos | familia | pareja

// Mínimo del campo fecha: hoy (el backend rechaza fechas pasadas con 422).
const fechaMin = hoyISO()

/* ------------------------------------------------------------------ *
 * Utilidades
 * ------------------------------------------------------------------ */

/** Fecha de hoy en local con formato AAAA-MM-DD (toISOString usaría UTC). */
function hoyISO() {
  const hoy = new Date()
  const mes = String(hoy.getMonth() + 1).padStart(2, '0')
  const dia = String(hoy.getDate()).padStart(2, '0')
  return `${hoy.getFullYear()}-${mes}-${dia}`
}

/** "2026-10-20" → "20 oct 2026" (mediodía local para no desplazar el día). */
function fechaLegible(valor) {
  if (!valor) return '—'
  const fecha = new Date(`${valor}T12:00:00`)
  if (Number.isNaN(fecha.getTime())) return valor
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }).format(fecha)
}

// Resumen lateral: se recalcula solo mientras se escribe (nada se guarda).
const resumen = computed(() => ({
  destino: formulario.ciudad.trim() || '—',
  fecha: fechaLegible(formulario.fecha),
  personas: `${formulario.personas} ${formulario.personas === 1 ? 'persona' : 'personas'}`,
  gustos: formulario.gustos.trim() || '—',
  compania: etiquetaCompania() || '—',
}))

/* ------------------------------------------------------------------ *
 * Compañía (se envía dentro de gustos)
 * ------------------------------------------------------------------ */

function etiquetaCompania() {
  const opcion = OPCIONES_COMPANIA.find((item) => item.valor === compania.value)
  return opcion ? opcion.texto : ''
}

/** Una opción está disponible según el número de personas (RA-1 / RA-2). */
function companiaDisponible(valor) {
  const personas = Number(formulario.personas)
  if (!Number.isFinite(personas) || personas < 2) return false // sola persona: sin compañía
  if (valor === 'pareja' && personas > 2) return false // la pareja es exactamente 2
  return true
}

function elegirCompania(valor) {
  if (!companiaDisponible(valor)) return
  // Volver a pulsar la opción activa la quita.
  compania.value = compania.value === valor ? '' : valor
}

// Si cambian las personas y la selección deja de ser válida, se limpia.
watch(
  () => formulario.personas,
  () => {
    if (compania.value && !companiaDisponible(compania.value)) compania.value = ''
  },
)

/** Pista debajo de las opciones: explica por qué están desactivadas. */
const pistaCompania = computed(() => {
  const personas = Number(formulario.personas)
  if (!Number.isFinite(personas) || personas < 2) {
    return 'Con 1 persona no hace falta indicar compañía.'
  }
  if (personas === 2) return 'Sois dos: podéis elegir cualquiera.'
  return 'Opcional. «Pareja» solo se activa si sois exactamente dos.'
})

/** Texto de gustos que se envía de verdad: gustos + compañía (si la hay). */
const textoGustos = computed(() => {
  const base = formulario.gustos.trim()
  const opcion = OPCIONES_COMPANIA.find((item) => item.valor === compania.value)
  return opcion ? `${base} ${opcion.sufijo}`.trim() : base
})

/*
 * Formato del resultado.
 * La IA devuelve TEXTO plano con «Mañana: …», «Tarde: …» y «Noche: …».
 * Aquí solo se parte por esas etiquetas para pintar tres tarjetas: el contenido
 * se interpola con {{ }} (texto literal), NUNCA con v-html (R-14).
 * Si el texto no trae esas etiquetas, se muestra tal cual, sin romper nada.
 */
const plan = computed(() => {
  const texto = resultado.value
  if (!texto) return { intro: '', bloques: [] }

  const marcas = []
  const patron = /(mañana|tarde|noche)\s*:/gi
  let coincidencia = null
  while ((coincidencia = patron.exec(texto)) !== null) {
    const nombre = coincidencia[1].toLowerCase()
    marcas.push({
      titulo: nombre.charAt(0).toUpperCase() + nombre.slice(1),
      inicio: coincidencia.index,
      fin: coincidencia.index + coincidencia[0].length,
    })
  }

  // Sin al menos dos franjas reconocibles: texto completo, sin interpretar.
  if (marcas.length < 2) return { intro: '', bloques: [] }

  const bloques = marcas
    .map((marca, i) => ({
      titulo: marca.titulo,
      cuerpo: texto
        .slice(marca.fin, i + 1 < marcas.length ? marcas[i + 1].inicio : texto.length)
        .trim(),
    }))
    .filter((bloque) => bloque.cuerpo)

  return { intro: texto.slice(0, marcas[0].inicio).trim(), bloques }
})

/** Alterna entre tema oscuro (Figma) y claro. Solo en memoria. */
function cambiarTema() {
  temaOscuro.value = !temaOscuro.value
  document.documentElement.classList.toggle('claro', !temaOscuro.value)
}

/** Marca un campo como inválido y lo asocia a su input con aria-invalid. */
function marcarCampo(campo, mensaje) {
  erroresCampo[campo] = mensaje
}

function limpiarErroresCampo() {
  for (const campo of Object.keys(erroresCampo)) erroresCampo[campo] = ''
}

/** Primer campo inválido visible: recibe el foco para que el usuario lo corrija. */
function enfocarPrimerError() {
  const primerInvalido = document.querySelector('[aria-invalid="true"]')
  if (primerInvalido) primerInvalido.focus()
}

/* ------------------------------------------------------------------ *
 * Validación en cliente (ayuda al usuario; NO sustituye a la del backend)
 * ------------------------------------------------------------------ */

function validar() {
  limpiarErroresCampo()
  let correcto = true

  const ciudad = formulario.ciudad.trim()
  if (!ciudad) {
    marcarCampo('ciudad', 'Escribe la ciudad a la que vais.')
    correcto = false
  } else if (ciudad.length > LIMITES.ciudad) {
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

  // Los gustos se envían JUNTO con la compañía: se valida el texto final.
  if (!formulario.gustos.trim()) {
    marcarCampo('gustos', 'Cuéntanos qué os apetece (p. ej. «museos y tapas»).')
    correcto = false
  } else if (textoGustos.value.length > LIMITES.gustos) {
    marcarCampo(
      'gustos',
      `Los gustos, con la compañía indicada, superan los ${LIMITES.gustos} caracteres.`,
    )
    correcto = false
  }

  return correcto
}

/* ------------------------------------------------------------------ *
 * Envío al backend: POST /api/plan
 * ------------------------------------------------------------------ */

async function enviar() {
  // CA-RF01-02: mientras hay una petición en curso no se emite otra.
  if (estado.value === 'espera') return

  avisoGeneral.value = ''
  errorServidor.codigo = ''
  errorServidor.mensaje = ''

  // Sin datos válidos no se hace NINGUNA llamada de red (CA-RF01-03).
  if (!validar()) {
    estado.value = 'entrada'
    avisoGeneral.value = 'Revisa los campos marcados: no se ha enviado nada.'
    enfocarPrimerError()
    return
  }

  estado.value = 'espera'
  resultado.value = '' // un nuevo envío reemplaza al anterior (CA-RF04-01)

  try {
    const respuesta = await fetch(`${BASE_URL}/api/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ciudad: formulario.ciudad.trim(),
        fecha: formulario.fecha,
        personas: Number(formulario.personas),
        gustos: textoGustos.value, // gustos + compañía (p. ej. «museos (van con amigos)»)
      }),
    })

    const datos = await respuesta.json().catch(() => null)

    if (respuesta.ok) {
      // Solo se acepta el contrato {"resultado": "..."}.
      if (datos && typeof datos.resultado === 'string' && datos.resultado.trim()) {
        resultado.value = limpiarTexto(datos.resultado.trim())
        estado.value = 'resultado'
      } else {
        mostrarError('RESPUESTA_INESPERADA', 'El servidor ha devuelto una respuesta inesperada. Inténtalo de nuevo.')
      }
      return
    }

    if (respuesta.status === 422) {
      // Error de validación del backend: se marca campo a campo y sin llamar a la IA.
      manejar422(datos)
      return
    }

    // Errores controlados del contrato: 502 / 504 / 500…
    mostrarError(datos?.error?.codigo || 'ERROR_INTERNO', datos?.error?.mensaje || 'Error interno.')
  } catch {
    // fetch falla: backend caído o sin conexión.
    mostrarError('SIN_CONEXION', 'No se ha podido contactar con el servidor. Inténtalo más tarde.')
  }
}

function mostrarError(codigo, mensaje) {
  errorServidor.codigo = codigo
  errorServidor.mensaje = mensaje
  estado.value = 'error'
}

/**
 * Retoque final del texto de la IA: a veces el modelo añade un recuento de
 * palabras («…hasta tarde. (248 palabras)») porque el prompt pide un máximo.
 * Se quita ESE trozo final; el resto del plan se pinta tal cual llega.
 */
function limpiarTexto(texto) {
  return texto.replace(/\s*\(\s*\d+\s+palabras\s*\)\s*\.?$/i, '').trim()
}

/** Traduce el `detail` estándar de FastAPI/Pydantic a mensajes junto a cada campo. */
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
    // Cada elemento es {type, loc: ["body", "campo"], msg, ...}
    const campo = Array.isArray(item?.loc) ? item.loc[1] : null
    if (campo && mensajes[campo] && !erroresCampo[campo]) marcarCampo(campo, mensajes[campo])
  }

  const hayErrorDeCampo = Object.values(erroresCampo).some(Boolean)
  avisoGeneral.value = hayErrorDeCampo
    ? 'El backend ha rechazado los datos (422): revisa los campos marcados. No se ha llamado a la IA.'
    : 'El backend ha devuelto 422: revisa los datos del formulario.'

  estado.value = 'entrada'
  enfocarPrimerError()
}

/** Reintento desde el estado error: conserva el formulario y vuelve a enviar. */
function reintentar() {
  estado.value = 'entrada'
  enviar()
}

/** Vuelve al estado entrada sin perder los datos del formulario (CA-RF04-02). */
function editarFormulario() {
  estado.value = 'entrada'
}

/** Botón del estado resultado: deja la pantalla lista para un plan nuevo. */
function nuevoPlan() {
  resultado.value = ''
  estado.value = 'entrada'
}

/** Stepper de personas: nunca sale del rango del contrato. */
function cambiarPersonas(paso) {
  const actual = Number(formulario.personas) || LIMITES.personasMin
  formulario.personas = Math.min(LIMITES.personasMax, Math.max(LIMITES.personasMin, actual + paso))
}
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <!-- ── Cabecera ─────────────────────────────────────────────── -->
    <header class="border-b border-line">
      <div class="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div class="flex items-center gap-3">
          <span
            class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-acento text-acento-oscuro"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19V6a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v13" />
              <path d="M13 19h5a2 2 0 0 0 2-2v-5" />
              <circle cx="6.5" cy="17.5" r="1.5" />
              <circle cx="17.5" cy="10.5" r="1.5" />
            </svg>
          </span>
          <div class="leading-tight">
            <p class="text-sm font-extrabold">Planificador de itinerarios</p>
            <p class="text-xs text-muted">Tu día, organizado en segundos</p>
          </div>
        </div>

        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-full border border-line bg-card px-3 py-2 text-sm text-muted transition hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
          :aria-pressed="temaOscuro"
          @click="cambiarTema"
        >
          <svg
            v-if="temaOscuro"
            viewBox="0 0 24 24"
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" />
          </svg>
          <svg
            v-else
            viewBox="0 0 24 24"
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
          </svg>
          {{ temaOscuro ? 'Modo oscuro' : 'Modo claro' }}
        </button>
      </div>
    </header>

    <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-10 sm:px-6 sm:py-14">
      <!-- ── Presentación ───────────────────────────────────────── -->
      <section>
        <p
          class="inline-flex items-center gap-2 rounded-full border border-line bg-card px-3 py-1 text-xs text-muted"
        >
          <span class="h-2 w-2 rounded-full bg-ok" aria-hidden="true"></span>
          Sin registro · Gratis · Un plan en segundos
        </p>
        <h1 class="mt-4 text-4xl font-black tracking-tight sm:text-5xl">
          Tu plan de un día, <span class="text-acento">de la mañana a la noche</span>
        </h1>
        <p class="mt-3 max-w-2xl text-muted">
          Dinos a dónde vais, cuándo, cuántos sois y qué os apetece. La IA propone la
          mañana, la tarde y la noche; el resultado se muestra aquí mismo, sin registro y
          sin guardarlo en ningún sitio.
        </p>
      </section>

      <!-- ── Formulario + resumen ───────────────────────────────── -->
      <div class="mt-8 grid gap-6 lg:grid-cols-3">
        <form
          class="rounded-2xl border border-line bg-card p-5 sm:p-6 lg:col-span-2"
          novalidate
          @submit.prevent="enviar"
        >
          <h2 class="text-lg font-bold">Configura tu plan</h2>
          <p class="mt-1 text-sm text-muted">Los cuatro campos son obligatorios.</p>

          <div class="mt-6 grid gap-5 sm:grid-cols-2">
            <!-- Ciudad -->
            <div>
              <label for="ciudad" class="mb-1.5 block text-sm font-semibold">Ciudad</label>
              <input
                id="ciudad"
                v-model="formulario.ciudad"
                type="text"
                name="ciudad"
                autocomplete="off"
                :maxlength="LIMITES.ciudad"
                placeholder="Sevilla"
                class="w-full rounded-xl border bg-page px-3 py-2.5 text-ink placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                :class="erroresCampo.ciudad ? 'border-peligro' : 'border-line'"
                :aria-invalid="erroresCampo.ciudad ? 'true' : undefined"
                aria-describedby="error-ciudad"
                @input="erroresCampo.ciudad = ''"
              />
              <p v-if="erroresCampo.ciudad" id="error-ciudad" class="mt-1.5 text-xs text-peligro">
                {{ erroresCampo.ciudad }}
              </p>
            </div>

            <!-- Fecha -->
            <div>
              <label for="fecha" class="mb-1.5 block text-sm font-semibold">Fecha</label>
              <input
                id="fecha"
                v-model="formulario.fecha"
                type="date"
                name="fecha"
                :min="fechaMin"
                class="w-full rounded-xl border bg-page px-3 py-2.5 text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                :class="erroresCampo.fecha ? 'border-peligro' : 'border-line'"
                :aria-invalid="erroresCampo.fecha ? 'true' : undefined"
                aria-describedby="error-fecha"
                @input="erroresCampo.fecha = ''"
              />
              <p v-if="erroresCampo.fecha" id="error-fecha" class="mt-1.5 text-xs text-peligro">
                {{ erroresCampo.fecha }}
              </p>
            </div>

            <!-- Personas -->
            <div>
              <label for="personas" class="mb-1.5 block text-sm font-semibold">Personas</label>
              <div
                class="flex items-center justify-between rounded-xl border px-2 py-1.5"
                :class="erroresCampo.personas ? 'border-peligro' : 'border-line'"
              >
                <button
                  type="button"
                  class="h-8 w-8 rounded-lg bg-page text-lg leading-none text-muted transition hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
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
                  inputmode="numeric"
                  :min="LIMITES.personasMin"
                  :max="LIMITES.personasMax"
                  class="w-14 bg-transparent text-center text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                  :aria-invalid="erroresCampo.personas ? 'true' : undefined"
                  aria-describedby="error-personas"
                  @input="erroresCampo.personas = ''"
                />
                <button
                  type="button"
                  class="h-8 w-8 rounded-lg bg-page text-lg leading-none text-muted transition hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                  aria-label="Añadir una persona"
                  @click="cambiarPersonas(1)"
                >
                  +
                </button>
              </div>
              <p v-if="erroresCampo.personas" id="error-personas" class="mt-1.5 text-xs text-peligro">
                {{ erroresCampo.personas }}
              </p>
            </div>

            <!-- Contador (ayuda visual, no guarda nada) -->
            <div class="flex items-end">
              <p class="w-full rounded-xl border border-dashed border-line px-3 py-2.5 text-sm text-muted">
                Sin registro · sin cookies · sin base de datos
              </p>
            </div>

            <!-- Compañía (no es un campo del contrato: viaja dentro de gustos) -->
            <fieldset class="sm:col-span-2">
              <legend class="mb-1.5 block text-sm font-semibold">¿Con quién vais?</legend>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="opcion in OPCIONES_COMPANIA"
                  :key="opcion.valor"
                  type="button"
                  class="inline-flex items-center gap-1.5 rounded-xl border px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                  :class="
                    !companiaDisponible(opcion.valor)
                      ? 'cursor-not-allowed border-dashed border-line bg-page/40 text-muted/40'
                      : compania === opcion.valor
                        ? 'border-acento bg-acento/15 text-acento'
                        : 'border-line bg-page text-muted hover:border-acento/60 hover:text-ink'
                  "
                  :aria-pressed="compania === opcion.valor"
                  :disabled="!companiaDisponible(opcion.valor)"
                  :title="companiaDisponible(opcion.valor) ? undefined : 'No disponible con este número de personas'"
                  @click="elegirCompania(opcion.valor)"
                >
                  <!-- Icono «no disponible»: se nota sin leer nada -->
                  <svg
                    v-if="!companiaDisponible(opcion.valor)"
                    viewBox="0 0 24 24"
                    class="h-3.5 w-3.5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.25"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="9" />
                    <path d="M6 6l12 12" />
                  </svg>
                  {{ opcion.texto }}
                </button>
              </div>
              <p class="mt-1.5 text-xs text-muted">{{ pistaCompania }}</p>
            </fieldset>

            <!-- Gustos -->
            <div class="sm:col-span-2">
              <div class="mb-1.5 flex items-center justify-between gap-3">
                <label for="gustos" class="block text-sm font-semibold">Gustos</label>
                <span
                  class="text-xs"
                  :class="textoGustos.length > LIMITES.gustos ? 'text-peligro' : 'text-muted'"
                >
                  {{ textoGustos.length }}/{{ LIMITES.gustos }}
                  <template v-if="compania"> (con compañía)</template>
                </span>
              </div>
              <textarea
                id="gustos"
                v-model="formulario.gustos"
                name="gustos"
                rows="3"
                :maxlength="LIMITES.gustos"
                placeholder="Museos, gastronomía y paseos…"
                class="w-full resize-y rounded-xl border bg-page px-3 py-2.5 text-ink placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
                :class="erroresCampo.gustos ? 'border-peligro' : 'border-line'"
                :aria-invalid="erroresCampo.gustos ? 'true' : undefined"
                aria-describedby="error-gustos"
                @input="erroresCampo.gustos = ''"
              ></textarea>
              <p v-if="erroresCampo.gustos" id="error-gustos" class="mt-1.5 text-xs text-peligro">
                {{ erroresCampo.gustos }}
              </p>
            </div>
          </div>

          <!-- Envío -->
          <button
            type="submit"
            class="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-acento px-5 py-3 font-bold text-acento-oscuro transition hover:brightness-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento focus-visible:ring-offset-2 focus-visible:ring-offset-card disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            :disabled="estado === 'espera'"
            :aria-busy="estado === 'espera'"
          >
            <svg
              v-if="estado === 'espera'"
              viewBox="0 0 24 24"
              class="h-4 w-4 animate-spin"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              aria-hidden="true"
            >
              <path d="M21 12a9 9 0 1 1-6.2-8.6" />
            </svg>
            <svg
              v-else
              viewBox="0 0 24 24"
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path d="m12 3 1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9L12 3Z" />
            </svg>
            {{ estado === 'espera' ? 'Generando…' : 'Generar plan' }}
          </button>
          <p class="mt-3 text-xs text-muted">
            Tardará unos segundos · gratis · sin registro
          </p>
        </form>

        <!-- Resumen en vivo (solo lectura, nada se almacena) -->
        <aside class="h-fit rounded-2xl border border-line bg-card p-5">
          <div class="flex items-center justify-between">
            <h2 class="flex items-center gap-2 text-lg font-bold">
              <span
                class="inline-flex h-7 w-7 items-center justify-center rounded-lg bg-card-2 text-acento"
                aria-hidden="true"
              >
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 6h16M4 12h10M4 18h7" />
                </svg>
              </span>
              Tu plan
            </h2>
            <span
              class="h-2.5 w-2.5 rounded-full"
              :class="estado === 'espera' ? 'bg-acento' : 'bg-ok'"
              aria-hidden="true"
            ></span>
          </div>

          <dl class="mt-4 space-y-3 text-sm">
            <div class="flex items-start justify-between gap-3">
              <dt class="text-muted">Destino</dt>
              <dd class="text-right font-semibold">{{ resumen.destino }}</dd>
            </div>
            <div class="flex items-start justify-between gap-3">
              <dt class="text-muted">Fecha</dt>
              <dd class="text-right font-semibold">{{ resumen.fecha }}</dd>
            </div>
            <div class="flex items-start justify-between gap-3">
              <dt class="text-muted">Personas</dt>
              <dd class="text-right font-semibold">{{ resumen.personas }}</dd>
            </div>
            <div class="flex items-start justify-between gap-3">
              <dt class="text-muted">Compañía</dt>
              <dd class="text-right font-semibold">{{ resumen.compania }}</dd>
            </div>
            <div class="flex items-start justify-between gap-3">
              <dt class="text-muted">Gustos</dt>
              <dd class="text-right font-semibold">{{ resumen.gustos }}</dd>
            </div>
          </dl>

          <hr class="my-4 border-line" />
          <p class="text-xs text-muted">
            Nada de esto se guarda: ni base de datos, ni historial, ni almacenamiento en el
            navegador. Al recargar la página todo desaparece.
          </p>
        </aside>
      </div>

      <!-- ── Zona de estados (solo uno visible) ─────────────────── -->
      <section class="mt-6" aria-live="polite">
        <!-- entrada -->
        <template v-if="estado === 'entrada'">
          <div
            v-if="avisoGeneral"
            role="alert"
            class="rounded-2xl border border-peligro bg-peligro-suave p-5 text-sm text-peligro"
          >
            {{ avisoGeneral }}
          </div>
          <div
            v-else
            class="rounded-2xl border border-dashed border-line p-8 text-center text-muted"
          >
            <svg
              viewBox="0 0 24 24"
              class="mx-auto h-8 w-8 text-acento"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              aria-hidden="true"
            >
              <path d="M4 19V6a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v13" />
              <path d="M13 19h5a2 2 0 0 0 2-2v-5" />
              <circle cx="6.5" cy="17.5" r="1.5" />
              <circle cx="17.5" cy="10.5" r="1.5" />
            </svg>
            <p class="mt-3 font-semibold">Aquí aparecerá tu plan</p>
            <p class="mt-1 text-sm">Rellena el formulario y pulsa «Generar plan».</p>
          </div>
        </template>

        <!-- espera -->
        <div
          v-else-if="estado === 'espera'"
          class="rounded-2xl border border-line bg-card p-8 text-center"
        >
          <svg
            viewBox="0 0 24 24"
            class="mx-auto h-8 w-8 animate-spin text-acento"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            aria-hidden="true"
          >
            <path d="M21 12a9 9 0 1 1-6.2-8.6" />
          </svg>
          <p class="mt-3 font-semibold">Generando tu plan…</p>
          <p class="mt-1 text-sm text-muted">
            La IA tarda unos segundos. No cierres la página.
          </p>
        </div>

        <!-- resultado -->
        <article
          v-else-if="estado === 'resultado'"
          class="rounded-2xl border border-line bg-card p-5 sm:p-6"
        >
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p class="text-xs uppercase tracking-wide text-muted">Plan de un día</p>
              <h2 class="text-xl font-bold">
                {{ resumen.destino }} · {{ resumen.fecha }}
              </h2>
            </div>
            <button
              type="button"
              class="rounded-xl border border-line px-4 py-2 text-sm font-semibold text-muted transition hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
              @click="nuevoPlan"
            >
              Nuevo plan
            </button>
          </div>

          <!-- El texto de la IA se pinta como TEXTO ({{ }}), nunca con v-html -->
          <template v-if="plan.bloques.length">
            <p v-if="plan.intro" class="mt-4 whitespace-pre-wrap text-[15px] leading-relaxed">
              {{ plan.intro }}
            </p>

            <!-- Una tarjeta por franja: Mañana · Tarde · Noche -->
            <div class="mt-4 space-y-3">
              <section
                v-for="bloque in plan.bloques"
                :key="bloque.titulo"
                class="rounded-xl border border-line bg-page p-4"
              >
                <h3
                  class="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-acento"
                >
                  <svg
                    v-if="bloque.titulo === 'Noche'"
                    viewBox="0 0 24 24"
                    class="h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    aria-hidden="true"
                  >
                    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
                  </svg>
                  <svg
                    v-else
                    viewBox="0 0 24 24"
                    class="h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="4" />
                    <path
                      d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"
                    />
                  </svg>
                  {{ bloque.titulo }}
                </h3>
                <p class="mt-2 whitespace-pre-wrap text-[15px] leading-relaxed">
                  {{ bloque.cuerpo }}
                </p>
              </section>
            </div>
          </template>

          <!-- Si la IA no sigue el formato, se muestra tal cual (sin interpretar) -->
          <p v-else class="mt-4 whitespace-pre-wrap text-[15px] leading-relaxed">{{ resultado }}</p>

          <p
            class="mt-5 rounded-xl border border-acento/40 bg-acento/10 p-3 text-xs text-muted"
          >
            <strong class="text-acento">Aviso:</strong> texto generado por IA, orientativo y no
            verificado. Comprueba lugares, horarios y precios antes de salir.
          </p>
        </article>

        <!-- error -->
        <div
          v-else
          role="alert"
          class="rounded-2xl border border-peligro/50 bg-peligro-suave p-6 text-center"
        >
          <span
            class="mx-auto inline-flex h-11 w-11 items-center justify-center rounded-full bg-peligro/15 text-peligro"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 9v4m0 4h.01M10.3 3.9 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
            </svg>
          </span>
          <h2 class="mt-3 text-xl font-bold">No hemos podido generar el plan</h2>
          <p class="mt-2 text-sm text-muted">{{ errorServidor.mensaje }}</p>
          <p
            class="mt-3 inline-block rounded-full border border-peligro/40 px-3 py-1 font-mono text-xs text-peligro"
          >
            {{ errorServidor.codigo }}
          </p>

          <div class="mt-5 flex flex-wrap justify-center gap-3">
            <button
              type="button"
              class="rounded-xl bg-acento px-5 py-2.5 font-bold text-acento-oscuro transition hover:brightness-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento focus-visible:ring-offset-2 focus-visible:ring-offset-card"
              @click="reintentar"
            >
              Reintentar
            </button>
            <button
              type="button"
              class="rounded-xl border border-line px-5 py-2.5 font-semibold text-muted transition hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acento"
              @click="editarFormulario"
            >
              Editar el formulario
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- ── Pie ──────────────────────────────────────────────────── -->
    <footer class="border-t border-line">
      <div
        class="mx-auto flex w-full max-w-6xl flex-col gap-1 px-4 py-6 text-xs text-muted sm:flex-row sm:items-center sm:justify-between sm:px-6"
      >
        <p><strong class="text-ink">Planificador de itinerarios</strong> · © 2026</p>
        <p>Contenido generado por IA · Oriéntalo siempre antes de salir</p>
      </div>
    </footer>
  </div>
</template>
