<template>
  <SectionBanner />
  <section class="full">
    <!-- loading/error status -->
    <AppStatus
      v-if="facetsStatus === 'error' || locationListStatus == 'error'"
      status="error"
    />
    <AppStatus
      v-else-if="facetsStatus === 'loading' || locationListStatus == 'loading'"
      status="loading"
    />
    <SectionMap
      v-else-if="facets && locationList"
      :facets="facets"
      :location-list="locationList"
    />
  </section>
  <SectionWelcome />
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { getFacets, getLocationList } from "@/api";
import AppStatus from "@/components/AppStatus.vue";
import SectionBanner from "@/pages/home/SectionBanner.vue";
import SectionMap from "@/pages/home/SectionMap.vue";
import SectionWelcome from "@/pages/home/SectionWelcome.vue";
import { useQuery } from "@/util/composables";

/** get "core" data once on page load */
const {
  query: loadFacets,
  data: facets,
  status: facetsStatus,
} = useQuery(getFacets, undefined);
const {
  query: loadLocationList,
  data: locationList,
  status: locationListStatus,
} = useQuery(getLocationList, undefined);

onMounted(loadFacets);
onMounted(loadLocationList);
</script>
