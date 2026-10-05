<script setup lang="ts">
import { onMounted, ref } from "vue";
import SectionMap from "@/pages/home/SectionMap.vue";

const height = ref("");

onMounted(() => {
  const header = document.querySelector("header")?.clientHeight || 0;
  height.value = `calc(100dvh - ${header}px)`;
});
</script>

<template>
  <section :style="{ height }" class="p-8">
    <SectionMap />
  </section>
</template>
