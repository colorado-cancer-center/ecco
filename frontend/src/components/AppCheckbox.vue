<template>
  <SwitchGroup>
    <div class="container">
      <Switch
        :model-value="modelValue"
        as="template"
        @update:model-value="
          (value: boolean) => emit('update:modelValue', value)
        "
      >
        <button>
          <font-awesome-icon :icon="modelValue ? faSquareCheck : faSquare" />
        </button>
      </Switch>
      <SwitchLabel class="label">{{ label }}</SwitchLabel>
    </div>
  </SwitchGroup>
</template>

<script setup lang="ts">
import { faSquare, faSquareCheck } from "@fortawesome/free-regular-svg-icons";
import { Switch, SwitchGroup, SwitchLabel } from "@headlessui/vue";

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

<style scoped>
.container {
  display: flex;
  flex-shrink: 0;
  align-items: stretch;
  min-height: 30px;
  border-radius: var(--rounded);
  transition: background var(--fast);
}

.container * {
  cursor: pointer;
}

.container:hover {
  background: var(--off-white);
}

.label {
  display: flex;
  flex-grow: 1;
  align-items: center;
  padding-left: 5px;
}

button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  background: none;
  color: var(--theme);
  font-size: 1.25em;
}

button:not(:focus-visible) {
  outline: none !important;
}
</style>
