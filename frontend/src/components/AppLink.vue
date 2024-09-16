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

const props = withDefaults(defineProps<Props>(), {
  external: undefined,
  newTab: undefined,
});

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

/** is link to internal route or external url */
const external = computed(() =>
  ["http:", "mailto:"].some((prefix) => props.to.startsWith(prefix)),
);

const component = computed(() => (external.value ? "a" : "router-link"));

const toAttr = computed(() => (external.value ? "href" : "to"));

const target = computed(() =>
  (props.newTab ?? external.value) ? "_blank" : "",
);
</script>

<style scoped>
.link:has(svg) {
  display: inline-flex;
  align-items: center;
  gap: 0.5em;
}
</style>
