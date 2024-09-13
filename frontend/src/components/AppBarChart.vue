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
  /** y-axis label formatter */
  yFormat?: (value: Value) => string;
  /** whether data is numbers or enumerated strings */
  enumerated?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  yFormat: (value: Value) =>
    typeof value === "number" ? value.toLocaleString() : (value ?? ""),
});

const chart = ref<ComponentInstance<typeof VChart>>();
const { width, height } = useElementSize(() => chart.value?.root);
watchEffect(() => {
  /** manually resize */
  chart.value?.resize({
    width: width.value ?? 200,
    height: height.value ?? 200,
  });
});

provide(THEME_KEY, "light");

const colorA = getCssVar("--accent-a");
const colorB = getCssVar("--accent-b");

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
    width: 100,
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
    formatter: props.yFormat,
  };

  if (props.enumerated) console.log(props.data);

  const symbolSize = 30;

  options.series = Object.entries(props.data).map(([name, data], index) => ({
    name,
    type: props.enumerated ? "pictorialBar" : "bar",
    barMinHeight: props.enumerated ? 0 : 10,
    symbol: "diamond",
    symbolPosition: "end",
    symbolSize: [symbolSize, symbolSize],
    symbolOffset: [(index - 0.5) * 125 + "%", "-50%"],
    color: [colorA, colorB][index],
    data: Object.values(data).filter((value) => value !== undefined),
  }));

  return options;
});
</script>

<style scoped>
.chart {
  width: 100%;
  height: unset;
}
</style>
