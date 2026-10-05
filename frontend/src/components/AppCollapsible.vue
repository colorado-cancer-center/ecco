<script setup lang="ts">
import { ref, useTemplateRef, watchEffect } from "vue";
import AppButton from "@/components/AppButton.vue";
import { endEvent, startEvent } from "@/pages/home/TheTour.vue";
import { useAutoHeight } from "@/util/composables";
import { sleep } from "@/util/misc";
import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/vue";
import { ChevronDown, ChevronUp } from "@lucide/vue";
import { useEventListener } from "@vueuse/core";

type Props = {
  label: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

const root = useTemplateRef("root");
const panel = useTemplateRef("panel");
const open = ref(false);

useAutoHeight(panel, open);

useEventListener(root, startEvent, () => (open.value = true));
useEventListener(root, endEvent, () => (open.value = false));

watchEffect(async () => {
  if (open.value === true) {
    await sleep(100);
    panel.value?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});
</script>

<template>
  <Disclosure>
    <div
      ref="root"
      class="flex flex-col rounded-md border bg-white transition"
      :class="open ? 'border-gray' : 'border-transparent'"
    >
      <DisclosureButton as="template">
        <AppButton ref="button" design="accent" @click="open = !open">
          {{ label }}
          <ChevronUp v-if="open" />
          <ChevronDown v-else />
        </AppButton>
      </DisclosureButton>
      <DisclosurePanel as="template" static :unmount="false">
        <div
          ref="panel"
          class="flex scroll-mt-12 flex-col gap-4 overflow-y-clip px-4 transition-all"
          :class="open ? 'py-4' : ''"
        >
          <slot />
        </div>
      </DisclosurePanel>
    </div>
  </Disclosure>
</template>
