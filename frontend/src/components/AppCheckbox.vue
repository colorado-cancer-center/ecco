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
        <button class="button">
          <font-awesome-icon :icon="modelValue ? faSquareCheck : faSquare" />
        </button>
      </Switch>
      <SwitchLabel class="label">
        {{ label }}
      </SwitchLabel>
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
  align-items: center;
  border-radius: var(--rounded);
  transition: background var(--fast);
}

.container:hover {
  background: var(--theme-light);
}

.button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  border: none;
  background: none;
  color: var(--dark-gray);
  font-size: 1.25em;
  cursor: pointer;
}

.button:not(:focus-visible) {
  outline: none !important;
}

.label {
  flex-grow: 1;
  padding: 5px;
  cursor: pointer;
}
</style>
