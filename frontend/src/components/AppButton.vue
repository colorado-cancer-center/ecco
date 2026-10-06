<script setup lang="ts">
import { computed } from "vue";
import AppLink from "@/components/AppLink.vue";

type Props = {
  to?: string;
  design?: "none" | "normal" | "accent";
};

const { to, design = "normal" } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const component = computed(() => (to ? AppLink : "button"));
</script>

<template>
  <component
    :is="component"
    class="inline-flex items-center justify-center gap-2 rounded-md p-2 leading-none no-underline"
    :class="[
      design === 'accent' &&
        'border-dark-gray bg-dark-gray text-white hover:border-black hover:bg-black',
      design === 'normal' &&
        'border border-light-gray bg-white text-black hover:border-black',
    ]"
    :to="to"
  >
    <slot />
  </component>
</template>
