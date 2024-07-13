<template>
  <SectionBanner />
  <section class="full">
    <!-- loading/error status -->
    <AppStatus v-if="status && status !== 'success'" :status="status" />
    <SectionMap v-if="facets" :facets="facets" />
  </section>
  <SectionWelcome />
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { getFacets } from "@/api";
import AppStatus from "@/components/AppStatus.vue";
import SectionBanner from "@/pages/home/SectionBanner.vue";
import SectionMap from "@/pages/home/SectionMap.vue";
import SectionWelcome from "@/pages/home/SectionWelcome.vue";
import { useQuery } from "@/util/composables";

/** get "core" data once on page load */
const {
  query: loadFacets,
  data: facets,
  status,
} = useQuery(getFacets, undefined);

onMounted(loadFacets);
</script>
