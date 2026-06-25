<script setup lang="ts">
import { SliderRange, SliderRoot, SliderThumb, SliderTrack } from "radix-vue";

type Props = {
  label: string;
  modelValue: number;
  min?: number;
  max?: number;
  step?: number;
};

const {
  label,
  modelValue,
  min = 0,
  max = 1,
  step = 0.05,
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();
</script>

<template>
  <label class="flex flex-col items-stretch gap-1">
    <span>{{ label }}</span>

    <SliderRoot
      :model-value="[modelValue]"
      :min="min"
      :max="max"
      :step="step"
      :as-child="true"
      @update:model-value="
        (value) => emit('update:modelValue', value?.[0] || min)
      "
    >
      <span
        class="relative mb-1 flex h-2 cursor-pointer items-center py-2 text-stone-600 transition hover:text-black"
      >
        <SliderTrack class="relative h-1 grow rounded-full bg-stone-300">
          <SliderRange class="absolute h-full rounded-full bg-current" />
        </SliderTrack>
        <SliderThumb :as-child="true">
          <div
            class="absolute size-4 rounded-full bg-current"
            :aria-label="label"
          />
        </SliderThumb>
      </span>
    </SliderRoot>
  </label>
</template>
