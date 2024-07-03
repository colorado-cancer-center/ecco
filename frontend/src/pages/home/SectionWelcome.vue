<template>
  <section>
    <p>
      Welcome to <b>ECCO</b>, an interactive resource for exploring cancer data
      in Colorado! With this tool, you can view per-region data for things like
      population, demographics, cancer burden, risk factors, cancer disparities,
      health behaviors, environmental exposures, and more. You can also see
      local resources for cancer prevention, screening, treatment, survivorship,
      and more.
    </p>

    <div class="buttons">
      <AppButton to="/about" :icon="faCircleInfo" :flip="true" :accent="true"
        >Learn more</AppButton
      >
      <AppButton
        to="/about#acknowledge"
        :icon="faScroll"
        :flip="true"
        :accent="true"
        >Acknowledge us</AppButton
      >
      <AppButton to="/contact" :icon="faComment" :accent="true"
        >Give us feedback</AppButton
      >
    </div>
  </section>
</template>

<script setup lang="ts">
import { faComment } from "@fortawesome/free-regular-svg-icons";
import { faCircleInfo, faScroll } from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
</script>
