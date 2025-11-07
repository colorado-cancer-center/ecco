<template>
  <AppButton :accent="copied" @click="onClick">
    <font-awesome-icon v-if="copied" :icon="faCheck" />
    <slot v-else />
  </AppButton>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { faCheck } from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";

type Props = {
  text: string;
};

const { text } = defineProps<Props>();

const copied = ref(false);

const onClick = async () => {
  await navigator.clipboard.writeText(text);
  copied.value = true;
  setTimeout(() => (copied.value = false), 1000);
};
</script>
