<template>
  <v-chart ref="chart" class="chart" :option="option" />
</template>

<script setup lang="ts">
import {
  computed,
  provide,
  ref,
  watchEffect,
  type ComponentInstance,
} from "vue";
import VChart, { THEME_KEY } from "vue-echarts";
import type { EChartsOption } from "echarts";
import { BarChart, PictorialBarChart } from "echarts/charts";
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { uniq } from "lodash";
import { useElementSize } from "@vueuse/core";
import type { Unit } from "@/api";
import { formatValue } from "@/util/math";
import { getCssVar } from "@/util/misc";

use([
  SVGRenderer,
  BarChart,
  PictorialBarChart,
  TitleComponent,
  GridComponent,
  TooltipComponent,
]);

type Value = number | string | undefined;

type Props = {
  /** chart title */
  title: string;
  /** chart data */
  data: Record<string, Record<string, Value>>;
  /** y-axis unit */
  unit?: Unit;
  /** whether data is numbers or enumerated strings */
  enumerated?: boolean;
};

const props = withDefaults(defineProps<Props>(), { unit: undefined });

const chart = ref<ComponentInstance<typeof VChart>>();
const { width } = useElementSize(() => chart.value?.root);
watchEffect(() => {
  /** manually resize to fit container */
  chart.value?.resize({
    width: width.value ?? 200,
  });
});

provide(THEME_KEY, "light");

/** get colors from css theme vars */
const colorA = getCssVar("--accent-a");
const colorB = getCssVar("--accent-b");

/** echarts options */
const option = computed(() => {
  const options: EChartsOption = {};

  options.animation = false;

  options.title = {};
  options.title.text = props.title;
  options.title.right = "center";
  options.title.top = 15;
  options.title.textStyle = { fontSize: 18 };
  options.title.subtextStyle = { fontSize: 16 };

  options.grid = {};
  options.grid.left = 60;
  options.grid.top = 80;
  options.grid.bottom = 60;
  options.grid.right = 50;

  options.xAxis = {
    type: "category",
    data: uniq(
      Object.values(props.data)
        .map((series) => Object.keys(series))
        .flat(),
    ),
  };
  options.xAxis.axisLabel = {
    interval: 0,
    width: 80,
    overflow: "break",
    color: "black",
    fontSize: 16,
  };

  options.yAxis = {};
  options.yAxis.type = props.enumerated ? "category" : "value";
  options.yAxis.axisLabel = {
    interval: props.enumerated ? 0 : undefined,
    color: "black",
    fontSize: 16,
    formatter: (value: Value) => formatValue(value ?? "", props.unit, true),
  };

  const symbolSize = 30;

  options.series = Object.entries(props.data).map(
    ([name, data], index, entries) => ({
      name,
      type: props.enumerated ? "pictorialBar" : "bar",
      data: Object.values(data).map((value) => ({
        value: value ?? (props.enumerated ? "?" : 0),
        itemStyle: value ? undefined : { color: "#00000020" },
        noData: value === undefined,
      })),
      color: [colorA, colorB][index],
      barMinHeight: props.enumerated ? 0 : 5,
      symbol: "diamond",
      symbolPosition: "end",
      symbolSize: [symbolSize, symbolSize],
      symbolOffset: [
        (index - (entries.length - 1) / 2) * 100 * 1.1 + "%",
        "-50%",
      ],
    }),
  );

  options.tooltip = {};
  options.tooltip.trigger = "item";
  options.tooltip.formatter = (params) => {
    if (Array.isArray(params)) return "";
    let {
      value,
      name,
      seriesName,
      // @ts-expect-error attaching custom meta field
      data: { noData },
    } = params;
    if (typeof value === "object") return "";
    if (noData) value = "No Data";
    else value = formatValue(value ?? "", props.unit);
    return [seriesName, name, value].join("<br>");
  };
  options.tooltip.transitionDuration = 0;
  options.tooltip.textStyle = { fontSize: 16 };

  return options;
});
</script>

<style scoped>
.chart {
  width: 100%;
  height: unset;
}
</style>
