<template>
  <header
    class="flex flex-wrap items-center justify-between gap-2 p-4 max-md:flex-col max-md:text-center"
  >
    <AppLink to="/" class="flex items-baseline gap-4 text-black">
      <span>
        <b>E</b><span class="font-light">xploring</span> <b>C</b
        ><span class="font-light">ancer in</span> <b>Co</b
        ><span class="font-light">lorado</span>
      </span>
      <span class="text-xs font-light text-dark-gray">
        University of Colorado Cancer Center
      </span>
    </AppLink>

    <nav class="flex flex-wrap justify-center gap-4 uppercase">
      <template v-for="(route, index) of routes" :key="index">
        <AppLink
          v-if="route.meta?.header"
          :to="route.path"
          :class="[
            'p-1',
            route.name === $route.name && 'border-b-2 text-black',
          ]"
        >
          {{ route.name }}
        </AppLink>
      </template>
    </nav>
  </header>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import { routes } from "@/pages";
</script>
