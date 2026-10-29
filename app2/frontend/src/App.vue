<script setup>
import { SignInButton, UserButton, useAuth } from '@clerk/vue'

// Consulta a Clerk para mostrar el control adecuado cuando termina de cargar.
const { isLoaded, isSignedIn } = useAuth()
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

    <!-- Presenta el propósito de la pantalla; el formulario se añadirá después. -->
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
    </main>
  </div>
</template>
