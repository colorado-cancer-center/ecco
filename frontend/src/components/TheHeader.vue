<template>
  <header>
    <div class="title">
      <h1>{{ title }}</h1>
      <a class="logo" :href="presentedByLink" target="_blank">
        <img src="@/assets/logo.png" :alt="`Presented by ${presentedBy}`" />
      </a>
    </div>

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
import { routes } from "@/views";

// project info
const {
  VITE_TITLE: title,
  VITE_PRESENTED_BY: presentedBy,
  VITE_PRESENTED_BY_LINK: presentedByLink,
} = import.meta.env;
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
  }
}

.title {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px 20px;
  text-align: center;
}

h1 {
  margin: 0;
  color: currentColor;
}

.logo {
  height: 1.5em;
}

.logo img {
  height: 100%;
}

nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
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
  bottom: -2px;
  left: 50%;
  height: 2px;
  background: currentColor;
  content: "";
  transition: inset var(--fast);
}

.nav-link:is(:hover, [data-active="true"])::after {
  right: 5px;
  left: 5px;
}
</style>
