<template>
  <input
    :value="modelValue"
    @input="
      (event) =>
        $emit(
          'update:modelValue',
          (event.currentTarget as HTMLInputElement).value,
        )
    "
    class="input"
  />
</template>

<script setup lang="ts">
type Props = {
  modelValue?: string;
};

defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

defineEmits<Emits>();
</script>

<style scoped>
.input {
  padding: 10px 15px;
  box-shadow: var(--shadow);
}
</style>
