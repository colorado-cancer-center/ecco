<script setup lang="ts">
import type { Component } from "vue";
import { useTemplateRef } from "vue";
import { X } from "@lucide/vue";
import { useElementSize } from "@vueuse/core";
import { omit } from "lodash";

defineOptions({ inheritAttrs: false });

type Props = {
  icon?: Component;
};

defineProps<Props>();

const modelValue = defineModel<string>({ required: true });

const sideElement = useTemplateRef("side");
const sideSize = useElementSize(sideElement, undefined, { box: "border-box" });
</script>

<template>
  <div
    class="relative flex grow rounded-md border border-light-gray bg-white transition hover:border-black"
    :class="$attrs.class"
  >
    <input
      v-bind="omit($attrs, 'class')"
      v-model="modelValue"
      class="size-full rounded-md p-2"
      :style="{ paddingRight: sideSize.width.value + 'px' }"
    />

    <div
      ref="side"
      class="absolute inset-y-0 right-0 aspect-square *:size-full"
    >
      <button v-if="modelValue" @click="modelValue = ''">
        <X />
      </button>
      <div v-else-if="icon" class="grid place-items-center text-gray">
        <component :is="icon" />
      </div>
    </div>
  </div>
</template>
