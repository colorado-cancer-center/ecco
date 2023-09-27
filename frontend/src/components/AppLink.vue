<template>
  <component
    :is="component"
    :to="component !== 'a' && to"
    :href="component === 'a' && to"
    :target="isExternal ? '_blank' : ''"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";

type Props = {
  to: string;
};

const props = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const component = computed(() => (isExternal.value ? "a" : "router-link"));

const isExternal = computed(() =>
  ["http:", "https:", "ftp:", "mailto:"].some(
    (prefix) => props.to?.startsWith(prefix),
  ),
);
</script>
