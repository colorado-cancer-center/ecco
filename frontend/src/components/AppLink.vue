<template>
  <component :is="component" :[toAttr]="to" :target="target" class="link">
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";

type Props = {
  /** internal route or external url to link to */
  to: string;
  /** force new tab or not */
  newTab?: boolean;
};

const { to, newTab = undefined } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

/** is link to internal route or external url */
const external = computed(() =>
  ["https:", "http:", "mailto:"].some((prefix) => to.startsWith(prefix)),
);

const component = computed(() =>
  to ? (external.value ? "a" : "router-link") : "span",
);

const toAttr = computed(() => (external.value ? "href" : "to"));

const target = computed(() => ((newTab ?? external.value) ? "_blank" : ""));
</script>

<style scoped>
.link:has(svg) {
  display: inline-flex;
  align-items: center;
  gap: 0.5em;
}
</style>
