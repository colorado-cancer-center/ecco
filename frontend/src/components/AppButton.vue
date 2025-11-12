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

const { to } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const component = computed(() => (to ? AppLink : "button"));
</script>

<style scoped>
.button {
  background: var(--light-gray);
  color: var(--black);
}

a.button {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 35px;
  padding: 5px 10px;
  gap: 10px;
  border-radius: var(--rounded);
  text-decoration: none;
}

.button:hover {
  background: var(--theme-light);
}

.accent {
  background: var(--dark-gray);
  color: var(--white);
}

.accent:hover {
  background: var(--theme);
  color: var(--black);
}

.square {
  min-width: 35px;
  min-height: 35px;
  padding: 0;
}
</style>
