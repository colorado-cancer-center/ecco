<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import { routes } from "@/pages";
</script>

<template>
  <header
    class="flex flex-wrap items-center justify-between gap-2 p-4 max-md:flex-col max-md:text-center"
  >
    <div
      class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-black"
    >
      <AppLink to="/">
        <b>E</b><span class="font-light">xploring</span> <b>C</b
        ><span class="font-light">ancer in</span> <b>Co</b
        ><span class="font-light">lorado</span>
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
