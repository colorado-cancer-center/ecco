<template>
  <footer>
    <a :href="sourceCode" target="_blank">Source Code</a>
    <a :href="license" target="_blank">License</a>
  </footer>
</template>

<script setup lang="ts">
// project info
const { VITE_SOURCE_CODE: sourceCode, VITE_LICENSE: license } = import.meta.env;
</script>

<style scoped>
footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  padding: 20px;
  gap: 20px;
}

footer a:hover {
  text-decoration: underline;
}
</style>
