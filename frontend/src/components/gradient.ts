import * as d3 from "d3";
import { range } from "lodash";
import type { Option } from "@/components/AppSelect.vue";

// a few pretty color gradient options
// from https://github.com/d3/d3-scale-chromatic
export const gradientOptions = (
  [
    "interpolateCool",
    "interpolateViridis",
    "interpolatePlasma",
    "interpolateTurbo",

    "interpolatePuBuGn",
    "interpolatePuBu",
    "interpolateGnBu",
    "interpolateYlGnBu",
    "interpolateYlOrRd",
    "interpolatePuRd",
    "interpolateRdPu",
    "interpolateOrRd",

    "interpolateBlues",
    "interpolateGreens",
    "interpolateOranges",
    "interpolatePurples",
    "interpolateReds",
    "interpolateGreys",

    "interpolateSpectral",
    "interpolateRdYlGn",
    "interpolateRdYlBu",
    "interpolateRdBu",
    "interpolatePiYG",
    "interpolatePuOr",
    "interpolatePRGn",
  ] satisfies Extract<keyof typeof d3, `interpolate${string}`>[]
).map((key) => {
  const func = d3[key];
  const name = key.replace("interpolate", "");
  const id = name.toLowerCase();
  const colors = range(0, 1.01, 0.1).map(func);
  return { key, func, id, name, colors };
}) satisfies Option[];

// available gradient function names
export type GradientName = (typeof gradientOptions)[number]["key"];

// available gradient functions
export type GradientFunc = (typeof gradientOptions)[number]["func"];
