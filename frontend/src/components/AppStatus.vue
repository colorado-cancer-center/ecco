<template>
  <div class="my-10 flex items-center justify-center gap-2 p-4 shadow-md">
    <component
      :is="code.icon"
      :style="{ color: code.color }"
      :class="code.class"
    />
    <slot />
    <span>{{ code.text }}</span>
  </div>
</template>

<script setup lang="ts">
import type { Component } from "vue";
import { computed } from "vue";
import { CheckCircle, Cog, Info, XCircle } from "@lucide/vue";

type Props = {
  status: Status;
};

const { status } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

type Code = {
  icon: Component;
  color: string;
  text: string;
  class?: string;
};

export type Status = keyof typeof codes;

const codes = {
  info: {
    icon: Info,
    text: "Info",
    color: "color-dark-gray",
  },
  loading: {
    icon: Cog,
    text: "Loading",
    color: "color-dark-gray",
    class: "animate-spin",
  },
  success: {
    icon: CheckCircle,
    text: "Success",
    color: "color-success",
  },
  error: {
    icon: XCircle,
    text: "Error",
    color: "color-error",
  },
};

const code = computed<Code>(() => codes[status] || codes.info);
</script>
