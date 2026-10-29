<script setup>
import { reactive, ref, watch } from 'vue'
import { SignInButton, UserButton, useAuth } from '@clerk/vue'

// Consulta a Clerk para mostrar el control adecuado cuando termina de cargar.
const { isLoaded, isSignedIn } = useAuth()

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
    errores.ciudad = 'Escribe una ciudad (máximo 80 caracteres).'
  }

  if (!formulario.fecha || formulario.fecha < hoy.value) {
    errores.fecha = 'Elige hoy o una fecha posterior.'
  }

  if (
    !Number.isInteger(formulario.personas) ||
    formulario.personas < 1 ||
    formulario.personas > 20
  ) {
    errores.personas = 'Indica un número entero de personas, de 1 a 20.'
  }

  if (gustosOriginales.length < 1) {
    errores.gustos = 'Cuéntanos tus gustos (máximo 200 caracteres).'
  } else if (datosSolicitud.gustos.length > 200) {
    errores.gustos = compania.value
      ? 'El texto supera los 200 caracteres al añadir la compañía elegida.'
      : 'Cuéntanos tus gustos (máximo 200 caracteres).'
  }

  return !Object.values(errores).some(Boolean)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <!-- La cabecera mantiene el acceso y la cuenta en la misma pantalla. -->
    <header class="border-b border-slate-200 bg-white">
      <div
        class="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-6"
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

        <form novalidate @submit.prevent="validarFormulario" class="mt-6 grid gap-5">
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
              v-if="errores.ciudad"
              id="error-ciudad"
              class="text-sm text-red-700"
              aria-live="polite"
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
              v-if="errores.fecha"
              id="error-fecha"
              class="text-sm text-red-700"
              aria-live="polite"
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
              v-if="errores.personas"
              id="error-personas"
              class="text-sm text-red-700"
              aria-live="polite"
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
                class="size-4 accent-blue-700"
              />
              Sin especificar
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-800">
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value="amigos"
                class="size-4 accent-blue-700"
              />
              Amigos
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-800">
              <input
                v-model="compania"
                type="radio"
                name="compania"
                value="familia"
                class="size-4 accent-blue-700"
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
                class="size-4 accent-blue-700"
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
              v-if="errores.gustos"
              id="error-gustos"
              class="text-sm text-red-700"
              aria-live="polite"
            >
              {{ errores.gustos }}
            </p>
          </div>

          <button
            type="submit"
            class="w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800"
          >
            Generar plan
          </button>
        </form>
      </section>
    </main>
  </div>
</template>
