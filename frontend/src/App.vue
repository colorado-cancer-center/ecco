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
import { appTitle } from "@/meta";

const route = useRoute();

watch(
  route,
  () => {
    /** update tab title */
    if (route.name) appTitle.value = [String(route.name) || ""];
  },
  { immediate: true, deep: true },
);
</script>
