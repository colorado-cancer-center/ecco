<template>
  <section
    ref="alert"
    class="overflow-y-clip transition-all"
    :class="open ? '' : 'py-0'"
    :aria-hidden="open"
  >
    <slot />
    <AppButton :accent="true" class="self-center" @click="onClick">
      Dismiss
      <X />
    </AppButton>
  </section>
</template>

<script setup lang="ts">
import { onMounted, useTemplateRef } from "vue";
import { useAutoHeight } from "@/util/composables";
import { X } from "@lucide/vue";
import { useSessionStorage } from "@vueuse/core";
import AppButton from "./AppButton.vue";

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** for debugging */
// window.sessionStorage.clear();

/** open state, persisted for duration of browser session */
const open = useSessionStorage("popup", true);

const alert = useTemplateRef("alert");

useAutoHeight(alert, open);

onMounted(() => {
  /** always remember dismissal in dev mode */
  if (import.meta.env.MODE === "development") return;

  /** https://stackoverflow.com/questions/5004978/check-if-page-gets-reloaded-or-refreshed-in-javascript */
  const refresh = window.performance
    .getEntriesByType("navigation")
    .filter((entry) => "type" in entry)
    .map(({ type }) => type)
    .includes("reload");

  /** if "soft" refresh, remember dismissal */
  if (refresh) return;

  /** reset to showing alert */
  open.value = true;
});

const onClick = () => {
  open.value = false;
  /** force map auto-height re-adjust */
  window.scrollBy({ top: 1 });
  window.scrollBy({ top: -1 });
};
</script>
