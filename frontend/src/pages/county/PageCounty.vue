<template>
  <section>
    <AppHeading level="1"
      >Data for {{ countyData?.name || route.params.id }}</AppHeading
    >

    <!-- loading/error status -->
    <template v-if="countyDataStatus === 'error' || geometryStatus == 'error'">
      <AppStatus status="error" />
    </template>
    <template
      v-else-if="countyDataStatus === 'loading' || geometryStatus == 'loading'"
    >
      <AppStatus status="loading" />
    </template>

    <template v-else>
      <AppMap ref="map" class="map w-full h-[400px]" :geometry="geometry" :highlight="id">
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
    </template>
  </section>

  <template v-if="countyDataStatus === 'success'">
    <section id="county" class="wide">
      <AppSelect
        v-model="filter"
        class="w-[300px] mx-auto"
        :options="filterOptions"
        label="Measures"
      />

      <p class="text-center">
        vs.
        <span class="state-label">Colorado</span>
      </p>

      <template v-if="filter === 'basic'">
        <p class="text-center">
          <strong>Population</strong>: &nbsp;&nbsp;
          <span class="county-label">
            {{
              formatValue(
                countyData?.categories.sociodemographics?.measures.Total
                  ?.value ?? "-",
              )
            }}
          </span>
        </p>
        <div class="charts">
          <AppBarChart
            v-for="(chart, index) in chartData"
            :key="index"
            :title="chart.title"
            :data="chart.data"
            :unit="chart.unit"
            :order="chart.order"
          />
        </div>
      </template>

      <div v-else-if="countyData && filter === 'all'" class="grid grid-cols-[repeat(auto-fit,minmax(min(400px,100%),1fr))] items-start gap-x-[60px] gap-y-10">
        <template
          v-for="(category, categoryKey) in countyData.categories"
          :key="categoryKey"
        >
          <div class="grid grid-cols-[1fr_max-content_10px_max-content] items-center gap-x-4 gap-y-2 [&>:first-child]:col-span-full">
            <div level="2" class="flex col-span-full items-center gap-2 font-bold">
              {{ category.label }}
            </div>

            <template
              v-for="(measure, measureKey) in category.measures"
              :key="measureKey"
            >
              <dt>{{ measure.label }}</dt>
              <dd
                v-tooltip="formatValue(measure.value, measure.unit)"
                class="county-label relative z-0 px-1 py-[2px] rounded-md text-center bg-accent-a-light"
              >
                {{ formatValue(measure.value, measure.unit, true) }}
              </dd>

              <template
                v-if="
                  measure.state_value !== undefined &&
                  measure.state_value !== null
                "
              >
                <span
                  v-if="measure.value > measure.state_value"
                  class="text-gray"
                  >{{ ">" }}</span
                >
                <span
                  v-else-if="measure.value < measure.state_value"
                  class="text-gray"
                  >{{ "<" }}</span
                >
                <span
                  v-else-if="measure.value === measure.state_value"
                  class="text-gray"
                  >{{ "=" }}</span
                >
              </template>

              <span v-else></span>
              <span
                v-if="
                  measure.state_value !== undefined &&
                  measure.state_value !== null
                "
                v-tooltip="formatValue(measure.state_value, measure.unit)"
                class="state-label relative z-0 px-1 py-[2px] rounded-md text-center bg-accent-b-light"
                aria-label="State value"
              >
                {{ formatValue(measure.state_value, measure.unit, true) }}
              </span>
              <span v-else></span>
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
import { fromPairs, mapValues, orderBy, startCase, toPairs } from "lodash";
import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { getCountyData, getGeo } from "@/api";
import AppBarChart from "@/components/AppBarChart.vue";
import AppButton from "@/components/AppButton.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppMap from "@/components/AppMap.vue";
import AppSelect from "@/components/AppSelect.vue";
import AppStatus from "@/components/AppStatus.vue";
import { appTitle } from "@/meta";
import { useQuery } from "@/util/composables";
import { formatValue } from "@/util/math";
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
} = useQuery(() => getGeo("counties", "us_fips"), undefined);

onMounted(loadGeometry);

/** get data for selected county */
const {
  query: loadCountyData,
  data: countyData,
  status: countyDataStatus,
} = useQuery(
  async () => {
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

/** get select chart data from county data */
const chartData = computed(() =>
  countyData.value
    ? basicMeasures.map(({ title, showStateLevel, measures }) => {
        /** full value info for each measure */
        const measureValues = Object.fromEntries(
          measures.map(([category, measure]) => [
            startCase(measure),
            countyData.value?.categories[category ?? ""]?.measures[
              measure ?? ""
            ],
          ]),
        );

        return {
          title,
          unit: Object.values(measureValues).find((value) => value?.unit)?.unit,
          order: Object.values(measureValues).find((value) => value?.order)
            ?.order,
          data: {
            County: mapValues(measureValues, (value) => value?.value),
            ...(showStateLevel && {
              State: mapValues(measureValues, (value) => value?.state_value),
            }),
          },
        };
      })
    : [],
);

/** update tab title */
watch(countyData, () => (appTitle.value = [countyData.value?.name ?? ""]));
</script>

<style scoped>
/* grid > first child spans 3 rows - can't express this as a Tailwind utility */
.grid > :first-child {
  grid-row: 1 / span 3;
}
</style>
