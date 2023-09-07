<script setup>
import AppNavbar from '@/components/AppNavbar.vue'
</script>

<template>
  <div id="trunk">
    <AppNavbar />

    <div id="content">
      <router-view></router-view>
    </div>
  </div>
</template>
