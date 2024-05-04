<template>
  <SectionBanner />
  <section class="full">
    <!-- loading/error status -->
    <AppStatus v-if="coreStatus !== 'success'" :status="coreStatus" />
    <SectionMap
      v-if="facets && locations"
      :facets="facets"
      :locations="locations"
    />
  </section>
  <SectionWelcome />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { getFacets, getLocations, type Facets, type Locations } from "@/api";
import AppStatus from "@/components/AppStatus.vue";
import type { Status } from "@/components/AppStatus.vue";
import SectionBanner from "@/pages/home/SectionBanner.vue";
import SectionMap from "@/pages/home/SectionMap.vue";
import SectionWelcome from "@/pages/home/SectionWelcome.vue";

const coreStatus = ref<Status>("loading");
const facets = ref<Facets>();
const locations = ref<Locations>();

/** get "core" data once on page load */
async function loadCore() {
  try {
    coreStatus.value = "loading";
    facets.value = await getFacets();
    locations.value = await getLocations();
    coreStatus.value = "success";
  } catch (error) {
    console.error(error);
    coreStatus.value = "error";
  }
}
loadCore();
</script>
