<template>
  <Disclosure v-slot="{ open }">
    <DisclosureButton as="template">
      <AppButton
        ref="button"
        :icon="open ? faAngleUp : faAngleDown"
        class="button"
        :accent="true"
      >
        {{ label }}
      </AppButton>
    </DisclosureButton>
    <DisclosurePanel class="panel">
      <slot />
    </DisclosurePanel>
  </Disclosure>
</template>

<script setup lang="ts">
import { faAngleDown, faAngleUp } from "@fortawesome/free-solid-svg-icons";
import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/vue";
import AppButton from "@/components/AppButton.vue";

type Props = {
  label: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style scoped>
.panel {
  display: contents;
}
</style>
