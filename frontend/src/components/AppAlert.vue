<template>
  <section
    :class="['alert', dismissed && 'dismissed']"
    :aria-hidden="dismissed"
  >
    <slot />
    <AppButton class="dismiss" :icon="faXmark" :accent="true" @click="onClick"
      >Dismiss</AppButton
    >
  </section>
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

function onClick() {
  dismissed.value = true;
  /** force map auto-height re-adjust */
  window.scrollBy({ top: 1 });
  window.scrollBy({ top: -1 });
}
</script>

<style scoped>
.alert {
  --col: 1500px;
  position: relative;
  height: calc-size(auto);
  height: calc-size(auto);
  padding: 40px max(calc((100% - var(--col)) / 2), 40px);
  background: var(--theme-light);
  text-align: center;
  transition:
    height var(--slow),
    padding var(--slow);
}

.dismissed {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
}

.alert > :first-of-type {
  margin-top: 0 !important;
}

.dismiss {
  margin-top: 20px;
}
</style>
