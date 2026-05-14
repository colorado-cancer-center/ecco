<template>
  <component
    :is="component"
    :class="[
      'inline-flex min-h-10 min-w-10 shrink-0 items-center justify-center gap-2 rounded-md p-2 no-underline',
      accent
        ? 'bg-stone-600 text-white hover:bg-stone-500'
        : 'bg-stone-200 text-black hover:bg-stone-100',
    ]"
    :to="to"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";
import AppLink from "@/components/AppLink.vue";

type Props = {
  to?: string;
  accent?: boolean;
};

const { to } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const component = computed(() => (to ? AppLink : "button"));
</script>
