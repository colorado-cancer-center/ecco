<template>
  <component
    :is="component"
    :class="{ button: true, square: !!icon && !$slots.default, accent }"
    :to="to"
  >
    <font-awesome-icon v-if="icon && !flip" :icon="icon" class="icon" />
    <slot />
    <font-awesome-icon v-if="icon && flip" :icon="icon" class="icon" />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { IconDefinition } from "@fortawesome/free-solid-svg-icons";
import AppLink from "@/components/AppLink.vue";

type Props = {
  icon?: IconDefinition;
  to?: string;
  flip?: boolean;
  accent?: boolean;
};

const props = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const component = computed(() => (props.to ? AppLink : "button"));
</script>

<style scoped>
.button {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  min-height: 35px;
  padding: 5px 10px;
  gap: 10px;
  border: none;
  border-radius: var(--rounded);
  background: var(--light-gray);
  font: inherit;
  line-height: var(--compact);
  text-decoration: none;
  overflow-wrap: anywhere;
  cursor: pointer;
  transition:
    color var(--fast),
    background var(--fast);
}

.button:hover {
  background: var(--gray);
}

.accent {
  background: var(--black);
  color: var(--white);
}

.accent:hover {
  background: var(--dark-gray);
}

.square {
  width: 35px;
  height: 35px;
  padding: 0;
}
</style>
