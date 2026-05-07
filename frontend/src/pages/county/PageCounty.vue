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
      <AppMap ref="map" class="map" :geometry="geometry" :highlight="id">
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
        class="select"
        :options="filterOptions"
        label="Measures"
      />

      <p class="center">
        <span class="county-label">{{ countyData?.name }}</span>
        vs.
        <span class="state-label">Colorado</span>
      </p>

      <template v-if="filter === 'basic'">
        <p class="center">
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

      <div v-else-if="countyData && filter === 'all'" class="grid">
        <template
          v-for="(category, categoryKey) in countyData.categories"
          :key="categoryKey"
        >
          <div class="cell">
            <div level="2" class="cell-heading">
              {{ category.label }}
            </div>

            <template
              v-for="(measure, measureKey) in category.measures"
              :key="measureKey"
            >
              <dt>{{ measure.label }}</dt>
              <dd
                v-tooltip="formatValue(measure.value, measure.unit)"
                class="county-label"
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
                  class="compare-symbol"
                  >{{ ">" }}</span
                >
                <span
                  v-else-if="measure.value < measure.state_value"
                  class="compare-symbol"
                  >{{ "<" }}</span
                >
                <span
                  v-else-if="measure.value === measure.state_value"
                  class="compare-symbol"
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
                class="state-label"
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
:deep(.map) {
  width: 100%;
  height: 400px;
}

.select {
  width: 300px;
  margin: 0 auto;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(400px, 100%), 1fr));
  align-items: flex-start;
  gap: 40px 60px;
}

.grid > :first-child {
  grid-row: 1 / span 3;
}

.cell {
  display: grid;
  grid-template-columns: 1fr max-content 10px max-content;
  align-items: center;
  gap: 10px 20px;
}

.cell-heading {
  display: flex;
  grid-column: 1 / -1;
  align-items: center;
  gap: 10px;
  font-weight: var(--bold);
}

.county-label,
.state-label {
  z-index: 0;
  position: relative;
  padding: 2px 5px;
  border-radius: var(--rounded);
  text-align: center;
}

.county-label {
  background: var(--accent-a-light);
}

.state-label {
  background: var(--accent-b-light);
}

.compare-symbol {
  color: var(--gray);
}
</style>
