<template>
  <section style="--content: 300">
    <AppHeading level="1" class="self-center">
      {{ data?.name || route.params.id }}
    </AppHeading>

    <div class="grid grid-cols-3 place-items-center gap-8 max-md:grid-cols-1">
      <template v-if="geometryStatus == 'error'">
        <AppStatus status="error" class="size-full" />
      </template>
      <template v-else-if="geometryStatus == 'loading'">
        <AppStatus status="loading" class="size-full" />
      </template>
      <AppMap
        v-else
        ref="map"
        class="aspect-video w-100 max-w-full"
        :geometry="geometry"
        :highlight="id"
      />

      <template v-if="dataStatus == 'error'">
        <AppStatus status="error" />
      </template>
      <template v-else-if="dataStatus == 'loading'">
        <AppStatus status="loading" />
      </template>
      <div class="flex flex-col items-start gap-8">
        <AppSelect
          v-model="filter"
          class="w-30"
          :options="filterOptions"
          label="Data"
        />

        <p class="text-center">
          <span class="rounded-md bg-lime-500/25 p-1">{{ data?.name }}</span>
          vs.
          <span class="rounded-md bg-sky-500/25 p-1">Colorado</span>
        </p>

        <p class="text-center">
          <strong>Population</strong>{{ " " }}
          <span class="rounded-md bg-lime-500/25 p-1">
            {{
              formatValue(
                data?.categories.sociodemographics?.measures.Total?.value ??
                  "-",
              )
            }}
          </span>
          vs.
          <span class="rounded-md bg-sky-500/25 p-1">
            {{
              formatValue(
                data?.categories.sociodemographics?.measures.Total
                  ?.state_value ?? "-",
              )
            }}
          </span>
        </p>
      </div>
    </div>
  </section>

  <section v-if="dataStatus === 'success'">
    <template v-if="filter === 'basic'">
      <div
        class="grid grid-cols-[repeat(auto-fit,minmax(min(--spacing(100),100%),1fr))] place-content-center place-items-center gap-16"
      >
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

    <div
      v-else-if="data && filter === 'all'"
      class="grid grid-cols-[repeat(auto-fit,minmax(min(--spacing(100),100%),1fr))] items-start gap-16"
    >
      <template
        v-for="(category, categoryKey) in data.categories"
        :key="categoryKey"
      >
        <div
          class="grid grid-cols-[1fr_max-content_10px_max-content] items-center gap-x-4 gap-y-2 *:first:col-span-full"
        >
          <div class="col-span-full flex items-center gap-2 font-bold">
            {{ category.label }}
          </div>

          <template
            v-for="(measure, measureKey) in category.measures"
            :key="measureKey"
          >
            <dt>{{ measure.label }}</dt>
            <dd
              v-tooltip="formatValue(measure.value, measure.unit)"
              class="relative z-0 rounded-md bg-lime-500/25 p-1 text-center"
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
                class="text-stone-300"
                >{{ ">" }}</span
              >
              <span
                v-else-if="measure.value < measure.state_value"
                class="text-stone-300"
                >{{ "<" }}</span
              >
              <span
                v-else-if="measure.value === measure.state_value"
                class="text-stone-300"
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
              class="relative z-0 rounded-md bg-sky-500/25 p-1 text-center"
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

<script setup lang="ts">
import { computed, onMounted, ref, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { getCountyData, getGeo } from "@/api";
import AppBarChart from "@/components/AppBarChart.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppMap from "@/components/AppMap.vue";
import AppSelect from "@/components/AppSelect.vue";
import AppStatus from "@/components/AppStatus.vue";
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

/** load geometry data to display on map */
const {
  query: loadGeometry,
  data: geometry,
  status: geometryStatus,
} = useQuery(() => getGeo("counties", "us_fips"), undefined);

onMounted(loadGeometry);

/** get data for selected county */
const {
  query: loadData,
  data,
  status: dataStatus,
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

/** page title */
watchEffect(() => (appTitle.value = [data.value?.name ?? ""]));

watch(() => route.params.id, loadData, { immediate: true });

/** get select chart data from county data */
const chartData = computed(() =>
  data.value
    ? basicMeasures.map(({ title, showStateLevel, measures }) => {
        /** full value info for each measure */
        const measureValues = Object.fromEntries(
          measures.map(([category, measure]) => [
            startCase(measure),
            data.value?.categories[category ?? ""]?.measures[measure ?? ""],
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
</script>
