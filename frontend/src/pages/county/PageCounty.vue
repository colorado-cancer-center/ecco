<template>
  <section style="--content: 300">
    <AppHeading level="1" class="self-center">
      {{ title }}
    </AppHeading>

    <div class="grid grid-cols-3 place-items-center gap-8 max-md:grid-cols-1">
      <AppMap
        ref="map"
        class="aspect-video w-100 max-w-full"
        :class="geographyStatus === 'loading' && 'animate-loading'"
        :geography="geography"
        :highlight="id"
      />

      <div
        class="flex flex-col items-start gap-8"
        :class="featureStatus === 'loading' && 'animate-loading'"
      >
        <AppSelect
          v-model="filter"
          class="w-30"
          :options="filterOptions"
          label="Data"
        />

        <p class="text-center">
          <span class="rounded-md bg-lime-500/25 p-1">{{ feature.label }}</span>
          vs.
          <span class="rounded-md bg-sky-500/25 p-1">Colorado</span>
        </p>

        <p class="text-center">
          <strong>Population</strong>{{ " " }}
          <span class="rounded-md bg-lime-500/25 p-1">
            {{
              formatValue(
                feature.statistics["sociodemographics;Total"]?.value ?? "-",
              )
            }}
          </span>
          vs.
          <span class="rounded-md bg-sky-500/25 p-1">
            {{
              formatValue(
                formatValue(
                  feature.statistics["sociodemographics;Total"]?.state_value ??
                    "-",
                ),
              )
            }}
          </span>
        </p>
      </div>
    </div>
  </section>

  <section :class="featureStatus === 'loading' && 'animate-loading'">
    <template v-if="filter === 'basic'">
      <div
        class="grid grid-cols-[repeat(auto-fit,minmax(min(--spacing(100),100%),1fr))] place-content-center place-items-center gap-16"
      >
      </div>
    </template>

    <div
      v-else-if="filter === 'all'"
      class="grid grid-cols-[repeat(auto-fit,minmax(min(--spacing(100),100%),1fr))] items-start gap-16"
    >
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { getFeature, getLevel } from "@/api";
import AppBarChart from "@/components/AppBarChart.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppMap from "@/components/AppMap.vue";
import AppSelect from "@/components/AppSelect.vue";
import { appTitle } from "@/meta";
import { useQuery } from "@/util/composables";
import { formatValue } from "@/util/math";
import { fromPairs, mapValues, orderBy, startCase, toPairs } from "lodash";
import basicMeasures from "./basic-measures.json";

const route = useRoute();

/** get fips of viewed county */
const id = computed(() => [route.params.id].flat()[0] ?? "");

/** measure filter options */
const filterOptions = [
  { id: "basic", label: "Basic" },
  { id: "all", label: "All" },
];

/** selected measure filter */
const filter = ref<(typeof filterOptions)[number]["id"]>(filterOptions[0]!.id);

/** load geography data */
const {
  query: loadGeography,
  data: geography,
  status: geographyStatus,
} = useQuery(() => getLevel("county"), {
  type: "FeatureCollection",
  features: [],
});
onMounted(loadGeography);

/** get all data for feature */
const {
  query: loadFeature,
  data: feature,
  status: featureStatus,
} = useQuery(
  async () => {
    const results = await getFeature(id.value);

    /** sort by number of entries for more balanced look */
    // results.categories = fromPairs(
    //   orderBy(
    //     toPairs(results.categories),
    //     ([, category]) => Object.keys(category.measures).length,
    //     ["desc"],
    //   ),
    // );

    return results;
  },
  { label: "", statistics: {} },
);
watch(() => route.params.id, loadFeature, { immediate: true });

const title = computed(() => feature.value?.label || id.value || "County");

/** page title */
watchEffect(() => (appTitle.value = [title.value]));
</script>
