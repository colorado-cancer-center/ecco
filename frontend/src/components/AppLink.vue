<template>
  <component
    :is="component"
    :[toAttr]="to"
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

const isExternal = computed(() =>
  ["http:", "https:", "mailto:"].some((prefix) => props.to.startsWith(prefix)),
);

const toAttr = computed(() => (isExternal.value ? "href" : "to"));

const component = computed(() => (isExternal.value ? "a" : "router-link"));
</script>
