<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
</script>

<template>
  <footer class="flex items-center justify-end gap-4 p-4 max-sm:flex-col">
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
