<script setup lang="ts">
import { computed, nextTick, onMounted, useTemplateRef } from "vue";
import {
  useMutationObserver,
  useResizeObserver,
  useScroll,
} from "@vueuse/core";

defineOptions({ inheritAttrs: false });

const scrollElement = useTemplateRef("scrollElement");

/** scroll state */
const { arrivedState } = useScroll(scrollElement);

/** gap of parent */
const gap = computed(() =>
  scrollElement.value
    ? parseInt(window.getComputedStyle(scrollElement.value).gap)
    : 0,
);

/** force scroll to update */
const update = async () => {
  await nextTick();
  scrollElement.value?.dispatchEvent(new Event("scroll"));
};

/** update scroll on some events that might affect scrollElement's scrollWidth/Height */
onMounted(update);
useResizeObserver(scrollElement, update);
useMutationObserver(scrollElement, update, { childList: true, subtree: true });
</script>

<template>
  <div v-bind="$attrs" ref="scrollElement" class="overflow-y-auto">
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
