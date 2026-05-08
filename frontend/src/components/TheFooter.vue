<template>
  <footer class="flex items-center justify-between gap-4 p-4 max-sm:flex-col">
    <AppLink to="https://medschool.cuanschutz.edu/colorado-cancer-center">
      <img src="@/assets/logo.png" class="h-10" :alt="'Presented by...'" />
    </AppLink>
    <span class="flex flex-wrap justify-center gap-4">
      <AppLink to="https://github.com/colorado-cancer-center/ecco">
        Source Code
      </AppLink>
      <AppLink
        to="https://github.com/colorado-cancer-center/ecco/blob/main/LICENSE"
      >
        License
      </AppLink>
    </span>
  </footer>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
</script>
