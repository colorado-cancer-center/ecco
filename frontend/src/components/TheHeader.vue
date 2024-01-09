<template>
  <header>
    <h1>
      <div>{{ pretitle }}</div>
      <div>{{ title }}</div>
    </h1>

    <nav>
      <router-link
        v-for="(route, index) of routes"
        :key="index"
        class="nav-link"
        :to="route.path"
        :data-active="route.name === $route.name"
      >
        {{ route.name }}
      </router-link>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { routes } from "@/pages";

/** project info */
const { VITE_PRETITLE: pretitle, VITE_TITLE: title } = import.meta.env;
</script>

<style scoped>
header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  gap: 10px;
}

@media (max-width: 800px) {
  header {
    flex-direction: column;
    text-align: center;
  }
}

h1 > :first-child {
  font-weight: var(--regular);
  font-size: 0.9rem;
}

nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  text-transform: uppercase;
}

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
