<template>
  <label class="label">
    <span v-if="!hideLabel">{{ label }}</span>
    <input
      class="input"
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

<style scoped>
.label {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
  cursor: pointer;
}

.input {
  min-height: 35px;
  padding: 5px 10px;
  border: none;
  border-radius: var(--rounded);
  background: var(--light-gray);
  font: inherit;
  transition: background var(--fast);
}

.input:hover {
  background: var(--theme-light);
}
</style>
