import type { Unit } from "@/api/index";
import { capitalize } from "@/util/string";

/** format map data value */
export function formatValue(
  value: number | string,
  unit?: Unit,
  compact = false,
): string {
  if (typeof value === "string") return capitalize(value);
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
}

/**
 * normalize value from [min, max] to [0, 1], apply math function to value, then
 * un-normalize
 */
export function normalizedApply(
  value: number,
  min: number,
  max: number,
  func: (value: number) => number,
) {
  /** normalize */
  value = (value - min) / (max - min);
  /** apply func */
  value = func(value);
  /** un-normalize */
  value = value * (max - min) + min;
  return value;
}
