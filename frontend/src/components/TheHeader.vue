<template>
  <header class="header">
    <AppLink to="/">
      <h1>
        <div class="pretitle">
          {{ pretitle }}
        </div>
        <div>
          <span class="title">
            <b>E</b>xploring <b>C</b>ancer in <b>Co</b>lorado
          </span>
          <span class="subtitle">ECCO</span>
        </div>
      </h1>
    </AppLink>

    <nav class="nav">
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
.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  gap: 10px;
}

@media (max-width: 800px) {
  .header {
    flex-direction: column;
    text-align: center;
  }
}

.pretitle {
  font-weight: var(--regular);
  font-size: 0.9rem;
  letter-spacing: 0.009em;
  opacity: 0.75;
}

.title {
  font-weight: var(--regular);
}

.title > b {
  font-weight: var(--extra-bold);
}

.subtitle {
  margin-left: 0.5em;
  font-size: 0.915rem;
  opacity: 0.5;
}

.nav {
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
