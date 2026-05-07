<template>
  <header class="flex flex-wrap items-center justify-between p-4 gap-2 max-[800px]:flex-col max-[800px]:text-center">
    <AppLink to="/">
      <div class="text-[0.9rem] tracking-[0.009em]">University of Colorado Cancer Center's</div>
      <div>
        <span class="title">
          <b class="font-[800]">E</b>xploring <b class="font-[800]">C</b>ancer in <b class="font-[800]">Co</b>lorado
        </span>
        <span class="text-[0.9rem] opacity-50">&nbsp;(ECCO)</span>
      </div>
    </AppLink>

    <nav class="flex flex-wrap justify-center gap-2 uppercase">
      <template v-for="(route, index) of routes" :key="index">
        <AppLink
          v-if="route.meta?.header"
          :to="route.path"
          class="nav-link"
          :data-active="route.name === $route.name"
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

<style scoped>
/* Animated underline for nav links */
.nav-link {
  display: flex;
  position: relative;
  align-items: center;
  padding: 5px 10px;
  gap: 10px;
  font-size: 1.1rem;
  text-decoration: none;
}

.nav-link::after {
  position: absolute;
  right: 50%;
  bottom: 2px;
  left: 50%;
  height: 2px;
  background: currentColor;
  content: "";
  transition: inset var(--fast);
}

.nav-link:is(:hover, [data-active="true"])::after {
  right: 8px;
  left: 8px;
}
</style>
