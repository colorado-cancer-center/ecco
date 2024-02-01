<template>
  <header>
    <AppLink to="/">
      <h1>
        <div>{{ pretitle }}</div>
        <div>
          <b>E</b>xploring <b>C</b>ancer in <b>Co</b>lorado (<b>ECCO</b>)
        </div>
      </h1>
    </AppLink>

    <nav>
      <AppLink
        v-for="(route, index) of routes"
        :key="index"
        :to="route.path"
        class="nav-link"
        :data-active="route.name === $route.name"
      >
        {{ route.name }}
      </AppLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import { routes } from "@/pages";

/** project info */
const { VITE_PRETITLE: pretitle } = import.meta.env;
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

h1 > :last-child {
  font-weight: var(--regular);
  text-transform: uppercase;
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
