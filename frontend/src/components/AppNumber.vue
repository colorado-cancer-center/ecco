<script setup lang="ts">
import { clamp } from "lodash";

type Props = {
  label: string;
  modelValue: number;
  min?: number;
  max?: number;
  step?: number;
  hideLabel?: boolean;
};

const {
  label,
  modelValue,
  min = 0,
  max = 1,
  step = 0.01,
  hideLabel = false,
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

/** emit model value to parent */
const onChange = (event: Event) => {
  let value = Number((event.target as HTMLInputElement).value);
  value = clamp(value, min, max);
  emit("update:modelValue", value);
};
</script>

<template>
  <label class="flex shrink-0 cursor-pointer flex-col items-stretch gap-1">
    <span v-if="!hideLabel">{{ label }}</span>
    <input
      class="rounded-md border-none bg-stone-200 p-2 transition hover:bg-stone-100"
      type="number"
      :value="modelValue"
      :min="min"
      :max="max"
      :step="step"
      :aria-label="label"
      @change="onChange"
    />
  </label>
</template>
