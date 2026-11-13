<script setup lang="ts">
import { Square, SquareCheck } from "@lucide/vue";
import { SwitchRoot } from "reka-ui";

type Props = {
  label: string;
};

defineProps<Props>();

const checked = defineModel<boolean>();
</script>

<template>
  <label
    class="flex cursor-pointer items-center rounded-md border border-light-gray bg-white p-1 transition hover:border-black"
  >
    <SwitchRoot
      v-model="checked"
      as="button"
      type="button"
      class="flex cursor-pointer items-center justify-center border-none bg-transparent p-1 text-dark-gray not-focus-visible:outline-none"
    >
      <SquareCheck v-if="checked" />
      <Square v-else />
    </SwitchRoot>

    <div class="grow">
      {{ label }}
    </div>
  </label>
</template>
