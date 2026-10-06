<script setup lang="ts">
import { ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import { sleep } from "@/util/misc";
import { Check, Copy, LoaderCircle } from "@lucide/vue";

type Props = {
  text: string;
};

const { text } = defineProps<Props>();

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();

const status = ref("");

/** copy text to clipboard */
const copy = async () => {
  status.value = "copying";
  await navigator.clipboard.writeText(text);
  status.value = "copied";
  await sleep(1000);
  status.value = "";
};
</script>

<template>
  <AppButton v-if="text" class="size-8 shrink-0 p-0!" @click="copy">
    <LoaderCircle v-if="status === 'copying'" class="animate-spin" />
    <Check v-else-if="status === 'copied'" />
    <slot v-else-if="$slots.default" />
    <Copy v-else />
  </AppButton>
</template>
