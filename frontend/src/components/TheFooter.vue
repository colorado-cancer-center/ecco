<template>
  <footer class="flex items-center justify-between p-4 gap-4">
    <AppLink
      class="h-[2em]"
      to="https://medschool.cuanschutz.edu/colorado-cancer-center"
    >
      <img src="@/assets/logo.png" class="h-full" :alt="'Presented by...'" />
    </AppLink>
    <span class="flex flex-wrap justify-center gap-4">
      <AppLink
        class="hover:underline"
        to="https://github.com/colorado-cancer-center/ecco"
        >Source Code</AppLink
      >
      <AppLink
        class="hover:underline"
        to="https://github.com/colorado-cancer-center/ecco/blob/main/LICENSE"
        >License</AppLink
      >
    </span>
  </footer>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
</script>

<style scoped>
@media (max-width: 500px) {
  footer {
    flex-direction: column;
  }
}
</style>
