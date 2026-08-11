<script setup lang="ts">
/**
 * Screen header, shared by the eight portal screens.
 *
 * The nine screens each grew their own heading with `text-2xl` from Tailwind
 * rather than the system role, so the type scale the generator emits reached
 * the guide and stopped there: measured, the title to body ratio was 1.71 and
 * every heading rendered at weight 400. One component means the next screen
 * cannot repeat that.
 *
 * The rule on the left is the diagram world's way of saying "this is where the
 * current enters": it is the same mark the indicator card and the section
 * headings use, so the chrome stays one language.
 */
defineProps<{
  /** Screen title, already translated. */
  titulo: string
  /** One line on what the screen is for, already translated. */
  descripcion?: string
}>()
</script>

<template>
  <header class="flex flex-col gap-1 border-l-2 border-info pl-5">
    <h1 class="font-display text-titulo-1 text-corriente-pleno">
      {{ titulo }}
    </h1>
    <p v-if="descripcion" class="max-w-(--medida-maxima) text-cuerpo-amplio text-corriente-medio">
      {{ descripcion }}
    </p>
  </header>
</template>
