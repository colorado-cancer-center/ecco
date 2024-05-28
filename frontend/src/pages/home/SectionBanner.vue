<template>
  <AppAlert>
    <p>
      <strong>This site is still under development</strong>. Please
      <AppLink to="/contact">let us know how we can improve it</AppLink>! ECCO
      is intended to support research, community inquiries, and outreach
      activities. It should not be used to guide clinical decisions.
    </p>
  </AppAlert>
</template>

<script setup lang="ts">
import AppAlert from "@/components/AppAlert.vue";
import AppLink from "@/components/AppLink.vue";
</script>
