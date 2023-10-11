<template>
  <div class="status">
    <font-awesome-icon
      :icon="code.icon"
      :style="{ color: code.color }"
      :class="code.class"
    />
    <slot />
    <span>{{ code.text }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  faCheckCircle,
  faXmarkCircle,
} from "@fortawesome/free-regular-svg-icons";
import {
  faGear,
  faInfoCircle,
  type IconDefinition,
} from "@fortawesome/free-solid-svg-icons";

type Props = {
  status: Status;
};

const props = withDefaults(defineProps<Props>(), { status: "info" });

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

type Code = {
  icon: IconDefinition;
  color: string;
  text: string;
  class?: string;
};

export type Status = keyof typeof codes;

const codes = {
  info: {
    icon: faInfoCircle,
    color: "var(--gray)",
    text: "Info",
  },
  loading: {
    icon: faGear,
    color: "var(--gray)",
    text: "Loading",
    class: "fa-spin",
  },
  success: {
    icon: faCheckCircle,
    text: "Success",
    color: "#10b981",
  },
  error: {
    icon: faXmarkCircle,
    text: "Error",
    color: "#f43f5e",
  },
};

const code = computed<Code>(() => codes[props.status] || codes.info);
</script>

<style scoped>
.status {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 40px 0;
  padding: 20px;
  gap: 10px;
  box-shadow: var(--shadow);
}
</style>
