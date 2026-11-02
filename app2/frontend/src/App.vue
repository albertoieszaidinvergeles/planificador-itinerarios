<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { SignInButton, UserButton, useAuth, useClerk } from '@clerk/vue'

// Consulta a Clerk para mostrar el control adecuado cuando termina de cargar.
const { getToken, isLoaded, isSignedIn } = useAuth()
const clerk = useClerk()

// Mantiene en memoria el único estado de pantalla y la última respuesta.
const estadoPantalla = ref('entrada')
const respuestaPlan = ref(null)
const mensajeError = ref('')
const avisoGeneral = ref('')
const tituloResultado = ref(null)
// Botones que se sustituyen entre sí: guardarlos permite devolverles el foco.
const botonGenerar = ref(null)
const botonReintentar = ref(null)
let solicitudEnCurso = false

// Mueve el foco al elemento nuevo para que el teclado no pierda su posición.
watch(estadoPantalla, async (estado) => {
  if (estado === 'resultado') {
    await nextTick()
    tituloResultado.value?.focus()
  } else if (estado === 'error') {
    // El botón «Generar plan» desaparece: el foco pasa a «Reintentar».
    await nextTick()
    botonReintentar.value?.focus()
  }
})

// Mensajes de error de cada campo: los usa la validación del navegador y también el 422 del backend.
const mensajesValidacion = {
  ciudad: 'Escribe una ciudad (máximo 80 caracteres).',
  fecha: 'Elige hoy o una fecha posterior.',
  personas: 'Indica un número entero de personas, de 1 a 20.',
  gustos: 'Cuéntanos tus gustos (máximo 200 caracteres).',
}

// Prepara el plan para pintarlo: si trae «Mañana:», «Tarde:» y «Noche:» una vez y en orden, lo parte en
// tres tarjetas; si no, devuelve el texto completo (tramos: null) para mostrarlo sin dividir.
const resultadoPlan = computed(() => {
  const texto = respuestaPlan.value?.json?.resultado
  if (typeof texto !== 'string') {
    return null
  }

  const etiquetas = ['Mañana:', 'Tarde:', 'Noche:']
  const posiciones = etiquetas.map((etiqueta) => texto.indexOf(etiqueta))
  const etiquetasUnicas = etiquetas.every(
    (etiqueta) => texto.indexOf(etiqueta) === texto.lastIndexOf(etiqueta),
  )
  const ordenCorrecto = posiciones.every(
    (posicion, indice) =>
      posicion >= 0 && (indice === 0 || posicion > posiciones[indice - 1]),
  )

  if (!etiquetasUnicas || !ordenCorrecto) {
    return { texto, tramos: null }
  }

  const tramos = etiquetas.map((etiqueta, indice) => {
    const inicio = posiciones[indice] + etiqueta.length
    const fin = posiciones[indice + 1] ?? texto.length
    return texto.slice(inicio, fin).trim()
  })

  return {
    texto,
    tramos: [
      { titulo: 'Mañana', texto: tramos[0] },
      { titulo: 'Tarde', texto: tramos[1] },
      { titulo: 'Noche', texto: tramos[2] },
    ],
  }
})

// Formatea la fecha con el calendario local para no desplazarla por la zona horaria.
function obtenerFechaLocal() {
  const fecha = new Date()
  const anio = fecha.getFullYear()
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${anio}-${mes}-${dia}`
}

// Conserva en memoria los valores iniciales que utilizará el formulario.
const hoy = ref(obtenerFechaLocal())
const formulario = reactive({
  ciudad: '',
  fecha: hoy.value,
  personas: 1,
  gustos: '',
})

// Mantiene la compañía como una preferencia temporal independiente del formulario.
const compania = ref('')

// Borra la preferencia cuando deja de ser válida para el nuevo grupo de personas.
watch(
  () => formulario.personas,
  (personas) => {
    if (
      personas < 2 ||
      (compania.value === 'pareja' && personas !== 2)
    ) {
      compania.value = ''
    }
  },
)

// Mantiene los mensajes de validación asociados a cada campo.
const errores = reactive({
  ciudad: '',
  fecha: '',
  personas: '',
  gustos: '',
})

// Construye el cuerpo del contrato, incorporando la compañía solo al texto de gustos.
function construirDatosSolicitud() {
  const gustos = formulario.gustos.trim()
  const sufijosCompania = {
    amigos: '(van con amigos)',
    familia: '(van en familia)',
    pareja: '(van en pareja)',
  }
  const sufijo = sufijosCompania[compania.value]

  return {
    ciudad: formulario.ciudad.trim(),
    fecha: formulario.fecha,
    personas: formulario.personas,
    gustos: sufijo ? `${gustos} ${sufijo}` : gustos,
  }
}

// Comprueba todos los campos y comunica si los datos están listos para enviarse.
function validarFormulario() {
  // Actualiza el límite en la fecha local actual, incluso si cambió desde que se abrió.
  hoy.value = obtenerFechaLocal()

  errores.ciudad = ''
  errores.fecha = ''
  errores.personas = ''
  errores.gustos = ''

  const datosSolicitud = construirDatosSolicitud()
  const gustosOriginales = formulario.gustos.trim()

  if (datosSolicitud.ciudad.length < 1 || datosSolicitud.ciudad.length > 80) {
    errores.ciudad = mensajesValidacion.ciudad
  }

  if (!formulario.fecha || formulario.fecha < hoy.value) {
    errores.fecha = mensajesValidacion.fecha
  }

  if (
    !Number.isInteger(formulario.personas) ||
    formulario.personas < 1 ||
    formulario.personas > 20
  ) {
    errores.personas = mensajesValidacion.personas
  }

  if (gustosOriginales.length < 1) {
    errores.gustos = mensajesValidacion.gustos
  } else if (datosSolicitud.gustos.length > 200) {
    errores.gustos = compania.value
      ? 'El texto supera los 200 caracteres al añadir la compañía elegida.'
      : mensajesValidacion.gustos
  }

  return !Object.values(errores).some(Boolean)
}

// Abre el modal oficial de Clerk cuando la persona necesita autenticarse.
function abrirModalInicioSesion() {
  const instanciaClerk = clerk.value
  if (!instanciaClerk) {
    throw new Error('Clerk no está disponible para iniciar sesión.')
  }

  instanciaClerk.openSignIn()
}

// Solicita autenticación cuando hace falta y envía una única petición válida.
async function enviarFormulario() {
  if (
    estadoPantalla.value === 'espera' ||
    !isLoaded.value ||
    solicitudEnCurso
  ) {
    return
  }

  avisoGeneral.value = ''
  if (!validarFormulario()) {
    const primerCampoConError = ['ciudad', 'fecha', 'personas', 'gustos'].find(
      (campo) => errores[campo],
    )
    await nextTick()
    if (primerCampoConError) {
      document.getElementById(primerCampoConError)?.focus()
    }
    return
  }

  if (!isSignedIn.value) {
    abrirModalInicioSesion()
    return
  }

  solicitudEnCurso = true
  try {
    const token = await getToken.value()
    if (token === null) {
      abrirModalInicioSesion()
      return
    }

    respuestaPlan.value = null
    estadoPantalla.value = 'espera'

    const urlBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
    const respuesta = await fetch(`${urlBase}/api/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(construirDatosSolicitud()),
    })

    respuestaPlan.value = {
      codigoHttp: respuesta.status,
      json: await respuesta.json(),
    }

    if (respuesta.status === 200) {
      const resultado = respuestaPlan.value.json?.resultado
      if (typeof resultado !== 'string' || !resultado.trim()) {
        mensajeError.value = 'No se ha podido mostrar el plan. Inténtalo de nuevo.'
        estadoPantalla.value = 'error'
        return
      }

      estadoPantalla.value = 'resultado'
    } else if (respuesta.status === 422) {
      const detalles = respuestaPlan.value.json?.detail
      let hayCampoDesconocido = !Array.isArray(detalles) || detalles.length === 0

      for (const detalle of Array.isArray(detalles) ? detalles : []) {
        const campo = Array.isArray(detalle?.loc)
          ? detalle.loc[detalle.loc.length - 1]
          : null
        if (Object.hasOwn(mensajesValidacion, campo)) {
          errores[campo] = mensajesValidacion[campo]
        } else {
          hayCampoDesconocido = true
        }
      }

      if (hayCampoDesconocido) {
        avisoGeneral.value = 'Algunos datos no son válidos. Revisa el formulario.'
      }
      estadoPantalla.value = 'entrada'
    } else if (respuesta.status === 401) {
      avisoGeneral.value =
        'Tu sesión no es válida o ha caducado. Inicia sesión de nuevo y pulsa «Generar plan».'
      estadoPantalla.value = 'entrada'
    } else {
      const mensajeServidor = respuestaPlan.value.json?.error?.mensaje
      const codigoConMensaje = [500, 502, 504].includes(respuesta.status)
      mensajeError.value = codigoConMensaje
        && typeof mensajeServidor === 'string'
        && mensajeServidor.trim()
        ? mensajeServidor
        : 'Ha ocurrido un error. Inténtalo más tarde.'
      estadoPantalla.value = 'error'
    }
  } catch {
    mensajeError.value =
      'No se ha podido conectar con el servidor. Comprueba tu conexión e inténtalo de nuevo.'
    estadoPantalla.value = 'error'
  } finally {
    solicitudEnCurso = false
    if (estadoPantalla.value === 'espera') {
      estadoPantalla.value = 'error'
    }
  }
}

// Vuelve al formulario para que la persona decida si quiere enviar de nuevo.
async function reintentar() {
  mensajeError.value = ''
  estadoPantalla.value = 'entrada'
  // «Reintentar» desaparece: el foco vuelve a «Generar plan».
  await nextTick()
  botonGenerar.value?.focus()
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <!-- La cabecera mantiene el acceso y la cuenta en la misma pantalla. -->
    <header class="border-b border-slate-200 bg-white">
      <div
        class="mx-auto flex max-w-5xl flex-col items-start justify-between gap-4 px-4 py-4 sm:flex-row sm:items-center sm:px-6"
      >
        <p class="text-lg font-bold tracking-tight text-slate-900">
          Planificador de turismo
        </p>

        <!-- Espera a Clerk antes de ofrecer el acceso o la cuenta activa. -->
        <div v-if="isLoaded">
          <UserButton v-if="isSignedIn" />
          <SignInButton v-else mode="modal">
            <button
              type="button"
              class="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800"
            >
              Iniciar sesión con Google
            </button>
          </SignInButton>
        </div>
        <p v-else role="status" class="text-sm text-slate-600">
          Comprobando sesión…
        </p>
      </div>
    </header>

    <!-- Presenta el propósito y los campos para preparar el día de turismo. -->
    <main class="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
      <section class="mx-auto max-w-2xl text-center">
        <p class="text-sm font-semibold uppercase tracking-wide text-blue-700">
          Tu próxima aventura
        </p>
        <h1 class="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Planifica un día de turismo
        </h1>
        <p class="mt-4 text-base leading-7 text-slate-600">
          Prepara una jornada a tu medida y descubre qué hacer por la mañana, la
          tarde y la noche.
        </p>
      </section>

      <!-- Recoge los datos y presenta errores propios, sin activar validación del navegador. -->
      <section
        class="mx-auto mt-10 max-w-2xl rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8"
        aria-labelledby="formulario-titulo"
      >
        <h2 id="formulario-titulo" class="text-xl font-semibold">
          Cuéntanos qué tienes en mente
        </h2>

        <form novalidate @submit.prevent="enviarFormulario" class="mt-6 grid gap-5">
          <div class="grid gap-2">
            <label for="ciudad" class="text-sm font-medium text-slate-800">
              Ciudad
            </label>
            <input
              id="ciudad"
              v-model="formulario.ciudad"
              name="ciudad"
              type="text"
              required
              minlength="1"
              maxlength="80"
              autocomplete="address-level2"
              :aria-invalid="Boolean(errores.ciudad)"
              :aria-describedby="errores.ciudad ? 'error-ciudad' : undefined"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            />
            <p
              id="error-ciudad"
              aria-live="polite"
              :class="errores.ciudad ? 'break-words text-sm text-red-700' : 'sr-only'"
            >
              {{ errores.ciudad }}
            </p>
          </div>

          <div class="grid gap-2">
            <label for="fecha" class="text-sm font-medium text-slate-800">
              Fecha
            </label>
            <input
              id="fecha"
              v-model="formulario.fecha"
              name="fecha"
              type="date"
              :min="hoy"
              required
              :aria-invalid="Boolean(errores.fecha)"
              :aria-describedby="errores.fecha ? 'error-fecha' : undefined"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            />
            <p
              id="error-fecha"
              aria-live="polite"
              :class="errores.fecha ? 'break-words text-sm text-red-700' : 'sr-only'"
            >
              {{ errores.fecha }}
            </p>
          </div>

          <div class="grid gap-2">
            <label for="personas" class="text-sm font-medium text-slate-800">
              Número de personas
            </label>
            <input
              id="personas"
              v-model.number="formulario.personas"
              name="personas"
              type="number"
              min="1"
              max="20"
              step="1"
              required
              :aria-invalid="Boolean(errores.personas)"
              :aria-describedby="errores.personas ? 'error-personas' : undefined"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            />
            <p
              id="error-personas"
              aria-live="polite"
              :class="errores.personas ? 'break-words text-sm text-red-700' : 'sr-only'"
            >
              {{ errores.personas }}
            </p>
          </div>

          <!-- Solo ofrece compañía cuando el número de personas lo permite. -->
          <fieldset
            v-if="formulario.personas >= 2"
            class="grid gap-3"
          >
            <legend class="text-sm font-medium text-slate-800">
              ¿Con quién viajas?
            </legend>
            <label class="flex items-center gap-2 text-sm text-slate-800">
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value=""
                class="size-4 accent-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
              />
              Sin especificar
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-800">
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value="amigos"
                class="size-4 accent-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
              />
              Amigos
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-800">
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value="familia"
                class="size-4 accent-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
              />
              Familia
            </label>
            <label
              v-if="formulario.personas === 2"
              class="flex items-center gap-2 text-sm text-slate-800"
            >
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value="pareja"
                class="size-4 accent-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
              />
              Pareja
            </label>
          </fieldset>

          <div class="grid gap-2">
            <label for="gustos" class="text-sm font-medium text-slate-800">
              Gustos e intereses
            </label>
            <textarea
              id="gustos"
              v-model="formulario.gustos"
              name="gustos"
              minlength="1"
              maxlength="200"
              required
              rows="4"
              :aria-invalid="Boolean(errores.gustos)"
              :aria-describedby="errores.gustos ? 'error-gustos' : undefined"
              class="w-full resize-y rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            ></textarea>
            <p
              id="error-gustos"
              aria-live="polite"
              :class="errores.gustos ? 'break-words text-sm text-red-700' : 'sr-only'"
            >
              {{ errores.gustos }}
            </p>
          </div>

          <p
            id="aviso-general"
            aria-live="polite"
            :class="avisoGeneral ? 'break-words rounded-lg bg-amber-50 p-3 text-sm text-amber-900' : 'sr-only'"
          >
            {{ avisoGeneral }}
          </p>

          <div
            role="alert"
            :class="estadoPantalla === 'error' ? 'block break-words rounded-lg bg-red-50 p-4 text-sm text-red-800' : 'sr-only'"
          >
            {{ mensajeError }}
          </div>

          <span role="status" aria-live="polite" class="sr-only">
            {{ estadoPantalla === 'espera' ? 'Generando…' : '' }}
          </span>
          <button
            v-if="estadoPantalla !== 'error'"
            ref="botonGenerar"
            type="submit"
            :disabled="estadoPantalla === 'espera'"
            aria-label="Generar plan"
            :aria-describedby="avisoGeneral ? 'aviso-general' : undefined"
            class="w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:bg-blue-700"
          >
            <span
              v-show="estadoPantalla === 'espera'"
              aria-hidden="true"
              class="inline-flex items-center gap-2"
            >
              <span
                aria-hidden="true"
                class="size-4 animate-spin rounded-full border-2 border-current border-r-transparent"
              ></span>
              <span>Generando…</span>
            </span>
            <span v-show="estadoPantalla !== 'espera'">Generar plan</span>
          </button>
          <button
            v-else
            ref="botonReintentar"
            type="button"
            :aria-describedby="avisoGeneral ? 'aviso-general' : undefined"
            class="w-full break-words rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
            @click="reintentar"
          >
            Reintentar
          </button>
        </form>

        <section
          v-if="estadoPantalla === 'resultado' && resultadoPlan"
          class="mt-6 grid gap-4"
          aria-labelledby="resultado-titulo"
        >
          <h3
            id="resultado-titulo"
            ref="tituloResultado"
            tabindex="-1"
            class="break-words text-lg font-semibold"
          >
            Tu plan del día
          </h3>
          <div
            v-if="resultadoPlan.tramos"
            class="grid gap-4 sm:grid-cols-3"
          >
            <article
              v-for="tramo in resultadoPlan.tramos"
              :key="tramo.titulo"
              class="break-words rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200"
            >
              <h4 class="break-words font-semibold">{{ tramo.titulo }}</h4>
              <p class="mt-2 break-words whitespace-pre-line text-sm leading-6 text-slate-700">
                {{ tramo.texto }}
              </p>
            </article>
          </div>
          <p
            v-else
            class="break-words whitespace-pre-line text-sm leading-6 text-slate-700"
          >
            {{ resultadoPlan.texto }}
          </p>
          <p class="break-words text-sm text-slate-600">
            Texto generado por IA, orientativo; comprueba sitios y horarios
          </p>
        </section>
      </section>
    </main>
  </div>
</template>
