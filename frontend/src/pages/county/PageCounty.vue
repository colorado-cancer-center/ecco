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

type StatisticOrGroup =
  | { group: string; depth: number }
  | {
      label: string;
      value?: Value;
      compare?: string;
      state?: Value;
      unit?: Unit;
    };

/** statistic groups to flat list */
const flatGroups = computed(() => {
  const recurse = (
    groups: Groups = statisticGroups,
    depth = 0,
  ): StatisticOrGroup[] =>
    Object.entries(groups).flatMap(([statisticOrGroup, subgroups]) => {
      /** group heading */
      if (subgroups)
        return [
          { group: statisticOrGroup, depth },
          ...recurse(subgroups, depth + 1),
        ];

      /** statistic details */
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

      return [{ label, value, compare, state, unit }];
    });

  return recurse();
});
</script>

<template>
  <section class="[--content:200]">
    <AppHeading level="1" class="self-center">
      {{ title }}
    </AppHeading>

    <div class="grid grid-cols-2 gap-8 max-sm:grid-cols-1">
      <AppMap
        ref="map"
        class="aspect-4/3 h-full"
        :class="geographyStatus === 'loading' && 'animate-loading'"
        :geography="geography"
        :highlight="id"
      />

      <div
        class="flex flex-col items-start gap-8 self-center"
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
    v-if="filter === 'basic'"
    :class="featureStatus === 'loading' && 'animate-loading'"
  >
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
  </section>

  <section
    v-else-if="filter === 'all'"
    class="[--content:200]"
    :class="featureStatus === 'loading' && 'animate-loading'"
  >
    <div
      class="grid grid-cols-[1fr_max-content_max-content_max-content] items-center gap-1 text-center *:rounded-md *:p-1"
    >
      <template v-for="(statisticOrGroup, index) in flatGroups" :key="index">
        <template v-if="'group' in statisticOrGroup">
          <component
            :is="`h${statisticOrGroup.depth + 2}`"
            class="col-span-full text-left"
            :class="[
              statisticOrGroup.depth === 0 && 'not-first:mt-12 not-last:mb-4',
              statisticOrGroup.depth === 1 && 'not-first:mt-8 not-last:mb-2',
            ]"
          >
            {{ statisticOrGroup.group }}
          </component>
        </template>
        <template v-else>
          <span class="text-left">{{ statisticOrGroup.label }}</span>
          <span
            v-if="
              statisticOrGroup.value !== undefined &&
              statisticOrGroup.unit !== undefined
            "
            v-tooltip="
              formatValue(statisticOrGroup.value, statisticOrGroup.unit)
            "
            class="bg-lime-500/25"
          >
            {{
              formatValue(statisticOrGroup.value, statisticOrGroup.unit, true)
            }}
          </span>
          <span v-else />
          <span>{{ statisticOrGroup.compare }}</span>
          <span
            v-if="
              statisticOrGroup.state !== undefined &&
              statisticOrGroup.unit !== undefined
            "
            v-tooltip="
              formatValue(statisticOrGroup.state, statisticOrGroup.unit)
            "
            class="bg-sky-500/25"
          >
            {{
              formatValue(statisticOrGroup.state, statisticOrGroup.unit, true)
            }}
          </span>
          <span v-else />
        </template>
      </template>
    </div>
  </section>
</template>
