import { upperFirst } from "lodash";
import type { Unit } from "@/api/index";

/** format map data value */
export const formatValue = (
  value: number | string,
  unit?: Unit,
  compact = false,
): string => {
  if (typeof value === "string") return upperFirst(value);
  const format: Intl.NumberFormatOptions = {};
  format.notation = compact ? "compact" : "standard";
  format.maximumSignificantDigits = compact ? 2 : 5;
  let suffix = "";
  switch (unit) {
    case "percent":
      value *= 100;
      suffix = "%";
      break;
    case "count":
      format.maximumFractionDigits = 0;
      break;
    case "rate":
      break;
    case "dollar_amount":
      format.style = "currency";
      format.currency = "USD";
      break;
    case "rank":
      break;
    case "ordinal":
      break;
    case "least_most":
      break;
  }
  return value.toLocaleString(undefined, format) + suffix;
};

/**
 * normalize value from [min, max] to [0, 1], apply math function to value, then
 * un-normalize
 */
export const normalizedApply = (
  value: number,
  min: number,
  max: number,
  func: (value: number) => number,
) => {
  /** normalize */
  value = (value - min) / (max - min);
  /** apply func */
  value = func(value);
  /** un-normalize */
  value = value * (max - min) + min;
  return value;
};

/** round to specific multiple */
export const round = (
  value: number,
  multiple: number,
  method: "round" | "floor" | "ceil" = "round",
) => Math[method](value / multiple) * multiple;
