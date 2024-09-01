<template>
  <section>
    <AppHeading level="1"
      >Data for {{ countyData?.name || route.params.id }}</AppHeading
    >
  </section>

  <!-- loading/error status -->
  <section v-if="countyDataStatus === 'error' || geometryStatus == 'error'">
    <AppStatus status="error" />
  </section>
  <section
    v-else-if="countyDataStatus === 'loading' || geometryStatus == 'loading'"
  >
    <AppStatus status="loading" />
  </section>

  <template v-else>
    <section>
      <AppMap ref="map" class="map" :geometry="geometry">
        <template #popup="{ feature }">
          <!-- link to full data -->
          <AppButton
            :icon="faExternalLinkAlt"
            :to="`/county/${feature.id}`"
            :flip="true"
            :new-tab="true"
            >See All Data</AppButton
          >
        </template>
      </AppMap>
    </section>

    <section id="county" class="wide">
      <AppSelect
        v-model="filter"
        class="select"
        :options="filterOptions"
        label="Measures"
      />

      <div v-if="filteredCountyData" class="grid">
        <template
          v-for="(category, categoryKey) in filteredCountyData.categories"
          :key="categoryKey"
        >
          <div class="cell">
            <div class="heading">{{ category.label }}</div>
            <template
              v-for="(measure, measureKey) in category.measures"
              :key="measureKey"
            >
              <dt>{{ measure.label }}</dt>
              <dd>{{ formatValue(measure.value, measure.unit) }}</dd>
            </template>
          </div>
        </template>
      </div>
    </section>
  </template>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { cloneDeep, fromPairs, isEmpty, orderBy, toPairs } from "lodash";
import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { getCountyData, getGeo } from "@/api";
import AppButton from "@/components/AppButton.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppMap from "@/components/AppMap.vue";
import AppSelect from "@/components/AppSelect.vue";
import AppStatus from "@/components/AppStatus.vue";
import { appTitle } from "@/meta";
import { useQuery } from "@/util/composables";
import { formatValue } from "@/util/math";
import { waitFor } from "@/util/misc";
import basicMeasures from "./basic-measures.json";

const route = useRoute();
const map = ref<InstanceType<typeof AppMap>>();

/** get fips of viewed county */
const id = computed(() => [route.params.id].flat()[0] ?? "");

/** measure filter options */
const filterOptions = [
  { id: "basic", label: "Basic" },
  { id: "all", label: "All" },
];

/** selected measure filter */
const filter = ref<(typeof filterOptions)[number]["id"]>(filterOptions[0]!.id);

/** load geometry data to display on map */
const {
  query: loadGeometry,
  data: geometry,
  status: geometryStatus,
} = useQuery(async function () {
  return await getGeo("counties", "us_fips");
}, undefined);

onMounted(loadGeometry);

/** select county feature on map */
watch(
  geometry,
  async () => {
    (await waitFor(() => map.value))?.selectFeature(id.value);
  },
  { deep: true },
);

/** get data for selected county */
const {
  query: loadCountyData,
  data: countyData,
  status: countyDataStatus,
} = useQuery(
  async function () {
    if (!id.value) return;
    const results = await getCountyData(id.value);

    /** sort by number of entries for more balanced look */
    results.categories = fromPairs(
      orderBy(
        toPairs(results.categories),
        ([, category]) => Object.keys(category.measures).length,
        ["desc"],
      ),
    );

    return results;
  },
  { FIPS: "", name: "", categories: {} },
);

watch(() => route.params.id, loadCountyData, { immediate: true });

/** county data, with certain measures filtered out */
const filteredCountyData = computed(() => {
  const data = cloneDeep(countyData.value);

  /** filter by certain measures */
  if (filter.value === "basic")
    for (const [categoryKey, { measures }] of Object.entries(
      data?.categories ?? {},
    )) {
      for (const [measureKey, { label }] of Object.entries(measures))
        if (!basicMeasures.includes(label)) delete measures[measureKey];
      if (isEmpty(measures)) delete data?.categories[categoryKey];
    }

  return data;
});

/** update tab title */
watch(countyData, () => (appTitle.value = [countyData.value?.name ?? ""]));
</script>

<style scoped>
:deep(.map) {
  width: 100%;
  height: 500px;
}

.select {
  width: 300px;
  margin: 60px auto;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(400px, 100%), 1fr));
  align-items: flex-start;
  gap: 40px;
}

.grid > :first-child {
  grid-row: 1 / span 2;
}

.cell {
  display: grid;
  grid-template-columns: 2fr 1fr;
  align-items: center;
  gap: 10px 20px;
}

.heading {
  grid-column: 1 / -1;
  font-weight: var(--bold);
}
</style>
