<script setup lang="ts">
import { computed, nextTick, onMounted, useTemplateRef } from "vue";
import {
  useMutationObserver,
  useResizeObserver,
  useScroll,
} from "@vueuse/core";

defineOptions({ inheritAttrs: false });

const element = useTemplateRef("element");

/** scroll state */
const { arrivedState } = useScroll(element);

/** gap of parent */
const gap = computed(() =>
  element.value ? parseInt(window.getComputedStyle(element.value).gap) : 0,
);

/** force scroll to update */
const update = async () => {
  await nextTick();
  element.value?.dispatchEvent(new Event("scroll"));
};

/** update scroll on some events that might affect element's scrollWidth/Height */
onMounted(update);
useResizeObserver(element, update);
useMutationObserver(element, update, { childList: true, subtree: true });
</script>

<template>
  <div v-bind="$attrs" ref="element" class="overflow-y-auto">
    <div
      class="pointer-events-none sticky top-0 z-10 h-0"
      :class="arrivedState.top ? 'opacity-0' : 'opacity-25'"
      :style="{ marginBottom: `${-gap}px` }"
    >
      <div class="h-4 bg-linear-to-b from-black to-transparent" />
    </div>
    <slot />
    <div
      class="pointer-events-none sticky bottom-0 z-10 h-0"
      :class="arrivedState.bottom ? 'opacity-0' : 'opacity-25'"
      :style="{ marginTop: `${-gap}px` }"
    >
      <div
        class="h-4 -translate-y-full bg-linear-to-t from-black to-transparent"
      />
    </div>
  </div>
</template>
