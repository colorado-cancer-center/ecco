<template>
  <div
    class="relative flex min-w-0 rounded-md bg-light-gray transition hover:bg-theme-light"
    :class="$attrs.class"
  >
    <input
      v-bind="omit($attrs, 'class')"
      class="min-w-0 rounded-md p-2"
      :style="{ paddingRight: sideSize.width.value + 'px' }"
      :value="modelValue"
      @input="
        (event) =>
          $emit(
            'update:modelValue',
            (event.currentTarget as HTMLInputElement).value,
          )
      "
    />

    <div
      ref="side"
      class="absolute inset-y-0 right-0 aspect-square *:size-full"
    >
      <button v-if="modelValue" @click="$emit('update:modelValue', '')">
        <X />
      </button>
      <div v-else-if="icon" class="grid place-items-center text-gray">
        <component :is="icon" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from "vue";
import { useTemplateRef } from "vue";
import { X } from "@lucide/vue";
import { useElementSize } from "@vueuse/core";
import { omit } from "lodash";

defineOptions({ inheritAttrs: false });

type Props = {
  modelValue: string;
  icon?: Component;
};

defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

defineEmits<Emits>();

const sideElement = useTemplateRef("side");
const sideSize = useElementSize(sideElement, undefined, { box: "border-box" });
</script>
