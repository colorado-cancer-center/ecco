<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import { routes } from "@/pages";
</script>

<template>
  <header
    class="flex flex-wrap items-center justify-between gap-2 border-b-4 p-4 max-md:flex-col max-md:text-center"
  >
    <div class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
      <AppLink to="/" class="text-lg font-light [&_b]:font-bold">
        <b class="text-light-gold">E</b>xploring
        <b class="text-light-gold">C</b>ancer in
        <b class="text-light-gold">Co</b>lorado
      </AppLink>
      <AppLink
        to="https://medschool.cuanschutz.edu/colorado-cancer-center"
        class="flex items-center gap-2 text-xs font-light"
      >
        <img src="/icon.png" class="h-5" alt="" />
        University of Colorado Cancer Center
      </AppLink>
    </div>

    <nav class="flex flex-wrap justify-center gap-4 uppercase">
      <template v-for="(route, index) of routes" :key="index">
        <AppLink
          v-if="route.meta?.header"
          :to="route.path"
          :data-active="route.name === $route.name"
        >
          {{ route.name }}
        </AppLink>
      </template>
    </nav>
  </header>
</template>
