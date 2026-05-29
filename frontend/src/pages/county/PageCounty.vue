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

  <section
    class="[--content:9999]"
    :class="featureStatus === 'loading' && 'animate-loading'"
  >
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
      v-else-if="filter === 'all'"
      class="columns-4 gap-20 max-lg:columns-3 max-md:columns-2 max-sm:columns-1"
    >
      <div
        class="grid grid-cols-[1fr_max-content_max-content_max-content] items-center gap-1 text-center *:rounded-md *:p-1"
      >
        <template
          v-for="({ label, value, compare, state, unit }, index) in flatGroups"
          :key="index"
        >
          <template v-if="value === undefined && state === undefined">
            <strong class="col-span-full text-left">{{ label }}</strong>
          </template>
          <template v-else>
            <span class="text-left">{{ label }}</span>
            <span
              v-if="value !== undefined && unit !== undefined"
              v-tooltip="formatValue(value, unit)"
              class="bg-lime-500/25"
            >
              {{ formatValue(value, unit, true) }}
            </span>
            <span v-else />
            <span>{{ compare }}</span>
            <span
              v-if="state !== undefined && unit !== undefined"
              v-tooltip="formatValue(state, unit)"
              class="bg-sky-500/25"
            >
              {{ formatValue(state, unit, true) }}
            </span>
            <span v-else />
          </template>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Unit, Value } from "@/api";
import type { Groups } from "@/pages/home/SectionMap.vue";
import { computed, onMounted, ref, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { getFeature, getLevel } from "@/api";
import statisticGroups from "@/api/data/statistic-groups.json";
import statisticLabels from "@/api/data/statistic-labels.json";
import AppBarChart from "@/components/AppBarChart.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppMap from "@/components/AppMap.vue";
import AppSelect from "@/components/AppSelect.vue";
import { appTitle } from "@/meta";
import { useQuery } from "@/util/composables";
import { formatValue } from "@/util/math";
import { getValue } from "@/util/types";
import { fromPairs, isEmpty, toPairs } from "lodash";
import basic from "./basic.json";

const route = useRoute();

/** get fips of viewed county */
const id = computed(() => [route.params.id].flat()[0] ?? "");

/** statistic filter options */
const filterOptions = [
  { id: "basic", label: "Basic" },
  { id: "all", label: "All" },
];

/** selected statistic filter */
const filter = ref<(typeof filterOptions)[number]["id"]>(filterOptions[1]!.id);

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
} = useQuery(() => getFeature(id.value), { label: "", statistics: {} });
watch(() => route.params.id, loadFeature, { immediate: true });

const title = computed(() => feature.value?.label || id.value || "County");

/** page title */
watchEffect(() => (appTitle.value = [title.value]));

/** get select chart data from county data */
const chartData = computed(() =>
  !isEmpty(feature.value.statistics)
    ? basic.map(({ title, showStateLevel, statistics }) => {
        /** full value info for each statistic */
        const statisticValues = Object.fromEntries(
          statistics.map((statistic) => [
            statistic,
            feature.value.statistics[statistic],
          ]),
        );

        const unit = Object.values(statisticValues).find(
          (value) => value?.unit,
        )?.unit;

        const order = Object.values(statisticValues).find(
          (value) => value?.order,
        )?.order;

        const county = fromPairs(
          toPairs(statisticValues).map(([key, value]) => [
            getValue(statisticLabels, key) ?? key,
            value?.value,
          ]),
        );

        const state = showStateLevel
          ? fromPairs(
              toPairs(statisticValues).map(([key, value]) => [
                getValue(statisticLabels, key) ?? key,
                value?.state_value,
              ]),
            )
          : undefined;

        return {
          title,
          unit,
          order,
          data: {
            County: county,
            ...(showStateLevel && { State: state }),
          },
        };
      })
    : [],
);

/** statistic groups to flat list */
const flatGroups = computed(() => {
  const getTree = (
    groups: Groups = statisticGroups,
  ): {
    label: string;
    value?: Value;
    compare?: string;
    state?: Value;
    unit?: Unit;
  }[] =>
    Object.entries(groups).flatMap(([statisticOrGroup, subgroups]) => {
      const label =
        getValue(statisticLabels, statisticOrGroup) ?? statisticOrGroup;
      const value = feature.value.statistics[statisticOrGroup]?.value;
      const state = feature.value.statistics[statisticOrGroup]?.state_value;
      const compare =
        value !== undefined && state !== undefined
          ? value > state
            ? ">"
            : value < state
              ? "<"
              : "="
          : undefined;
      const unit = feature.value.statistics[statisticOrGroup]?.unit;
      return [
        { label, value, compare, state, unit },
        ...(subgroups ? getTree(subgroups) : []),
      ];
    });

  return getTree();
});
</script>
