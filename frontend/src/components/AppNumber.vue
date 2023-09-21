<template>
  <label>
    <span>{{ label }}</span>
    <input
      type="number"
      :value="modelValue"
      :min="min"
      :max="max"
      :step="step"
      @change="onChange"
    />
  </label>
</template>

<script setup lang="ts">
import { clamp } from "lodash";

type Props = {
  label: string;
  modelValue: number;
  min?: number;
  max?: number;
  step?: number;
};

const props = withDefaults(defineProps<Props>(), {
  min: 0,
  max: 1,
  step: 0.01,
});

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

// emit model value to parent
function onChange(event: Event) {
  let value = Number((event.target as HTMLInputElement).value);
  value = clamp(value, props.min, props.max);
  emit("update:modelValue", value);
}
</script>

<style scoped>
label {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
  cursor: pointer;
}

input {
  min-height: 30px;
  padding: 0 10px;
  border: none;
  border-radius: var(--rounded);
  background: var(--off-white);
  font: inherit;
  transition: background var(--fast);
}

input:hover {
  background: var(--light-gray);
}
</style>
