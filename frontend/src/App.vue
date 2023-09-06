<script setup>
import AppNavbar from './components/AppNavbar.vue'
</script>

<template>
  <div class="trunk">
    <AppNavbar />

    <div id="content">
      <router-view></router-view>
    </div>
  </div>
  
</template>

<style scoped>

</style>
