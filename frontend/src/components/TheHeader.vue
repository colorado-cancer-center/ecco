<template>
  <header class="header">
    <AppLink to="/">
      <div class="pretitle">University of Colorado Cancer Center's</div>
      <div>
        <span class="title">
          <b>E</b>xploring <b>C</b>ancer in <b>Co</b>lorado
        </span>
        <span class="subtitle">&nbsp;(ECCO)</span>
      </div>
    </AppLink>

    <nav class="nav">
      <template v-for="(route, key) of routes" :key="key">
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
  font-size: 0.9rem;
  letter-spacing: 0.009em;
}

.title > b {
  font-weight: var(--extra-bold);
}

.subtitle {
  font-size: 0.9rem;
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
