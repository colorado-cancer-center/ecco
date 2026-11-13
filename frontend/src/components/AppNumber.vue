<script setup lang="ts">
import { clamp } from "lodash";

type Props = {
  label: string;
  min?: number;
  max?: number;
  step?: number;
  hideLabel?: boolean;
};

const {
  label,
  min = 0,
  max = 1,
  step = 0.01,
  hideLabel = false,
} = defineProps<Props>();

const modelValue = defineModel<number>({ required: true });

/** emit model value to parent */
const onChange = (event: Event) => {
  let value = Number((event.target as HTMLInputElement).value);
  value = clamp(value, min, max);
  modelValue.value = value;
};
</script>

<template>
  <label class="flex shrink-0 cursor-pointer flex-col items-stretch gap-1">
    <span v-if="!hideLabel">{{ label }}</span>
    <input
      class="rounded-md border border-light-gray bg-white p-2 transition hover:border-black"
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
