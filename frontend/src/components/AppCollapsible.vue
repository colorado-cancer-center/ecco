<script setup lang="ts">
import { ref, useTemplateRef } from "vue";
import AppButton from "@/components/AppButton.vue";
import { useAutoHeight } from "@/util/composables";
import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/vue";
import { ChevronDown, ChevronUp } from "@lucide/vue";

type Props = {
  label: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

const panel = useTemplateRef("panel");
const open = ref(false);

useAutoHeight(panel, open);
</script>

<template>
  <Disclosure>
    <div
      class="flex flex-col rounded-md bg-stone-50 transition"
      :class="open && 'shadow-md'"
    >
      <DisclosureButton as="template">
        <AppButton ref="button" :accent="true" @click="open = !open">
          {{ label }}
          <ChevronUp v-if="open" />
          <ChevronDown v-else />
        </AppButton>
      </DisclosureButton>
      <DisclosurePanel as="template" static :unmount="false">
        <div
          ref="panel"
          class="flex flex-col gap-4 overflow-y-clip px-4 transition-all"
          :class="open ? 'py-4' : ''"
        >
          <slot />
        </div>
      </DisclosurePanel>
    </div>
  </Disclosure>
</template>
