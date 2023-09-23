<template>
  <button :class="{ square: !!icon && !hasText, accent }">
    <font-awesome-icon v-if="icon && !flip" :icon="icon" class="icon" />
    <span v-if="hasText">
      <slot />
    </span>
    <font-awesome-icon v-if="icon && flip" :icon="icon" class="icon" />
  </button>
</template>

<script setup lang="ts">
import { computed, useSlots } from "vue";
import type { IconDefinition } from "@fortawesome/free-solid-svg-icons";

type Props = {
  icon?: IconDefinition;
  flip?: boolean;
  accent?: boolean;
};

defineProps<Props>();

const hasText = computed(() => !!useSlots().default);
</script>

<style scoped>
button {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  min-height: 35px;
  padding: 5px 10px;
  gap: 10px;
  border: none;
  border-radius: var(--rounded);
  background: var(--off-white);
  color: var(--dark-gray);
  font: inherit;
  cursor: pointer;
  transition:
    color var(--fast),
    background var(--fast);
}

button:hover {
  background: var(--light-gray);
}

span {
  overflow-wrap: break-word;
}

.icon {
  color: var(--theme);
}

.accent {
  background: var(--theme);
  color: var(--white);
}

.accent:hover {
  background: var(--dark-gray);
}

.accent .icon {
  color: var(--white);
}

.square {
  width: 35px;
  height: 35px;
  padding: 0;
}
</style>
