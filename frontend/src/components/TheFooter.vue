<template>
  <footer>
    <a class="logo" :href="logoLink" target="_blank">
      <img src="@/assets/logo.png" :alt="'Presented by...'" />
    </a>
    <span class="links">
      <a :href="sourceCode" target="_blank">Source Code</a>
      <a :href="license" target="_blank">License</a>
    </span>
  </footer>
</template>

<script setup lang="ts">
/** project info */
const {
  VITE_LOGO_LINK: logoLink,
  VITE_SOURCE_CODE: sourceCode,
  VITE_LICENSE: license,
} = import.meta.env;
</script>

<style scoped>
footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  gap: 20px;
}

@media (max-width: 500px) {
  footer {
    flex-direction: column;
  }
}

.logo {
  height: 2em;
}

.logo img {
  height: 100%;
}

.links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.links a:hover {
  text-decoration: underline;
}
</style>
