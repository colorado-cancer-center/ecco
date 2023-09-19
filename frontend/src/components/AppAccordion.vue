<template>
  <Disclosure v-slot="{ open }">
    <DisclosureButton as="template">
      <AppButton :icon="open ? faAngleUp : faAngleDown">{{ label }}</AppButton>
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
</script>

<style scoped>
.panel {
  display: contents;
}
</style>
