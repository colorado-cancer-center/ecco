import * as d3 from "d3";
import { range } from "lodash";
import type { Option } from "@/components/AppSelect.vue";

/** a few pretty color gradient options */
/** from https://github.com/d3/d3-scale-chromatic */
export const gradientOptions = (
  [
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

    "interpolateCool",
    "interpolateViridis",
    "interpolatePlasma",
    "interpolateTurbo",

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
  const label = key.replace("interpolate", "");
  const id = label.toLowerCase();
  /** concat 1 to include end of range */
  const colors = range(0, 1, 0.1).concat([1]).map(func);
  return { key, func, id, label, colors };
}) satisfies Option[];

/** available gradient function names */
export type GradientName = (typeof gradientOptions)[number]["key"];

/** available gradient functions */
export type GradientFunc = (typeof gradientOptions)[number]["func"];

/** get gradient interpolator function from shorthand id/name */
export function getGradient(id: string) {
  return (
    gradientOptions.find((option) => option.id === id)?.func ||
    d3.interpolateCool
  );
}
