<template>
  <TheHeader />
  <main>
    <router-view />
  </main>
  <TheFooter />
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import TheFooter from "@/components/TheFooter.vue";
import TheHeader from "@/components/TheHeader.vue";

/** project info */
const { VITE_TITLE: title } = import.meta.env;

const route = useRoute();

watch(
  route,
  () => {
    /** update tab title */
    document.title = [String(route.name || ""), title]
      .filter(Boolean)
      .join(" | ");
  },
  { immediate: true },
);
</script>

<style scoped></style>
