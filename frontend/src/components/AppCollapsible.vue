<script setup lang="ts">
import { ref, useTemplateRef, watchEffect } from "vue";
import AppButton from "@/components/AppButton.vue";
import { endEvent, startEvent } from "@/pages/home/TheTour.vue";
import { useAutoHeight } from "@/util/composables";
import { sleep } from "@/util/misc";
import { ChevronDown, ChevronUp } from "@lucide/vue";
import { useEventListener } from "@vueuse/core";
import {
  CollapsibleContent,
  CollapsibleRoot,
  CollapsibleTrigger,
} from "reka-ui";

type Props = {
  label: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

const rootElement = useTemplateRef<HTMLDivElement>("rootElement");
const panelElement = useTemplateRef<HTMLDivElement>("panelElement");
const open = ref(false);

useAutoHeight(panelElement, open);

useEventListener(rootElement, startEvent, () => (open.value = true));
useEventListener(rootElement, endEvent, () => (open.value = false));

watchEffect(async () => {
  if (open.value === true) {
    /** wait for auto-height open animation to finish */
    await sleep(500);
    panelElement.value?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }
});
</script>

<template>
  <CollapsibleRoot
    ref="rootElement"
    v-model:open="open"
    :unmount-on-hide="false"
    class="flex flex-col rounded-md border bg-white transition"
    :class="open ? 'border-gray' : 'border-transparent'"
  >
    <CollapsibleTrigger as-child>
      <AppButton design="accent">
        {{ label }}
        <ChevronUp v-if="open" />
        <ChevronDown v-else />
      </AppButton>
    </CollapsibleTrigger>
    <CollapsibleContent force-mount>
      <div
        ref="panelElement"
        class="flex scroll-mt-12 flex-col gap-4 overflow-y-clip px-4 transition-all"
        :class="open ? 'py-4' : ''"
      >
        <slot />
      </div>
    </CollapsibleContent>
  </CollapsibleRoot>
</template>
