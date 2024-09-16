<template>
  <footer class="footer">
    <AppLink
      class="logo"
      to="https://medschool.cuanschutz.edu/colorado-cancer-center"
    >
      <img src="@/assets/logo.png" :alt="'Presented by...'" />
    </AppLink>
    <span class="links">
      <AppLink to="https://github.com/colorado-cancer-center/ecco"
        >Source Code</AppLink
      >
      <AppLink
        to="https://github.com/colorado-cancer-center/ecco/blob/main/LICENSE"
        >License</AppLink
      >
    </span>
  </footer>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
</script>

<style scoped>
.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  gap: 20px;
}

@media (max-width: 500px) {
  .footer {
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
