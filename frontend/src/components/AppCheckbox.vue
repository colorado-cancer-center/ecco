<template>
  <SwitchGroup>
    <div
      class="flex min-h-10 items-center rounded-md transition hover:bg-theme-light"
    >
      <Switch
        :model-value="modelValue"
        as="template"
        @update:model-value="
          (value: boolean) => emit('update:modelValue', value)
        "
      >
        <button
          class="flex cursor-pointer items-center justify-center border-none bg-transparent p-1 text-dark-gray not-focus-visible:outline-none"
        >
          <SquareCheck v-if="modelValue" />
          <Square v-else />
        </button>
      </Switch>
      <SwitchLabel class="grow cursor-pointer p-1">
        {{ label }}
      </SwitchLabel>
    </div>
  </SwitchGroup>
</template>

<script setup lang="ts">
import { Switch, SwitchGroup, SwitchLabel } from "@headlessui/vue";
import { Square, SquareCheck } from "@lucide/vue";

type Props = {
  label: string;
  modelValue: boolean;
};

defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();
</script>
