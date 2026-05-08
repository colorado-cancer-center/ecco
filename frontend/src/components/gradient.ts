import type { Option } from "@/components/AppSelect.vue";
import * as d3 from "d3";
import { range } from "lodash";

type InterpolationFunc = Extract<keyof typeof d3, `interpolate${string}`>;

export const defaultGradient = "ylgnbu";

/** a few pretty color gradient options */
/** from https://github.com/d3/d3-scale-chromatic */
export const gradientOptions = (
  [
    /** basic */
    ["interpolateGreys", "Greys"],

    /** reds / oranges */
    ["interpolateReds", "Reds"],
    ["interpolateOranges", "Oranges"],
    ["interpolateOrRd", "Orange Red"],
    ["interpolateYlOrRd", "Yellow Orange Red"],

    /** greens / blues */
    ["interpolateGreens", "Greens"],
    ["interpolateGnBu", "Green Blue"],
    ["interpolateYlGnBu", "Yellow Green Blue"],
    ["interpolatePuBuGn", "Purple Blue Green"],
    ["interpolateBlues", "Blues"],
    ["interpolatePuBu", "Purple Blue"],

    /** purples / pinks */
    ["interpolatePurples", "Purples"],
    ["interpolatePuRd", "Purple Red"],
    ["interpolateRdPu", "Red Purple"],

    /** diverging */
    ["interpolateRdYlGn", "Red Yellow Green"],
    ["interpolateRdYlBu", "Red Yellow Blue"],
    ["interpolateRdBu", "Red Blue"],
    ["interpolatePiYG", "Pink Yellow Green"],
    ["interpolatePuOr", "Purple Orange"],
    ["interpolatePRGn", "Purple Red Green"],

    /** special */
    ["interpolatePlasma", "Plasma"],
    ["interpolateViridis", "Viridis"],
    ["interpolateCool", "Cool"],
    ["interpolateSpectral", "Spectral"],
    ["interpolateTurbo", "Turbo"],
  ] satisfies [InterpolationFunc, string][]
).map(([key, label]) => {
  /** get interpolate func */
  const func = d3[key];
  /** unique id, e.g. for syncing selected gradient with url */
  const id = key.replace("interpolate", "").toLowerCase();
  /** concat 1 to include end of range */
  const colors = range(0, 1, 0.1).concat([1]).map(func);
  return { key, func, id, label, colors };
}) satisfies Option[];

/** available gradient function names */
export type GradientName = (typeof gradientOptions)[number]["key"];

/** available gradient functions */
export type GradientFunc = (typeof gradientOptions)[number]["func"];

/** get gradient interpolator function from shorthand id/name */
export const getGradient = (id: string) =>
  gradientOptions.find((option) => option.id === id)?.func ||
  d3.interpolateCool;
