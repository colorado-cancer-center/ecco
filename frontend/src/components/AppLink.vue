<template>
  <component
    :is="component"
    :[toAttr]="to"
    :target="newTab ?? isExternal ? '_blank' : ''"
    class="link"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";

type Props = {
  to: string;
  newTab?: boolean;
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

<style scoped>
.link {
  display: inline-flex;
  align-items: center;
  gap: 0.5em;
}
</style>
