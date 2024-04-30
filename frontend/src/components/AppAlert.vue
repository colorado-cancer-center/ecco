<template>
  <div v-if="!dismissed" class="alert">
    <slot />
    <AppButton
      v-tooltip="'Dismiss'"
      class="button"
      :icon="faXmark"
      aria-label="Dismiss"
      @click="dismissed = true"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import AppButton from "./AppButton.vue";

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

const dismissed = ref(false);
</script>

<style scoped>
.alert {
  display: flex;
  position: relative;
  flex-direction: column;
  padding: 30px max(40px, (100% - 800px) / 2);
  gap: 10px;
  background: var(--theme-light);
}

.alert > :deep(*) {
  margin: 0;
}

.button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
}
</style>
