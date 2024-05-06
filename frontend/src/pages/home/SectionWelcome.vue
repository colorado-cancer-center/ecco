<template>
  <section>
    <p>
      Welcome to
      <b>E</b>xploring <b>C</b>ancer in <b>Co</b>lorado (<b>ECCO</b>), an
      interactive resource for exploring cancer data in Colorado. You can view
      per-region data for things like population, demographics, cancer burden,
      risk factors, cancer disparities, health behaviors, environmental
      exposures, and more. You can also see local resources for cancer
      prevention, screening, treatment, survivorship, and more.
    </p>

    <div class="buttons">
      <AppButton to="/about" :icon="faArrowRight" :flip="true" :accent="true"
        >Learn more</AppButton
      >
      <AppButton
        to="/about#acknowledge"
        :icon="faArrowRight"
        :flip="true"
        :accent="true"
        >Acknowledge Us</AppButton
      >
    </div>
  </section>
</template>

<script setup lang="ts">
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
</script>
