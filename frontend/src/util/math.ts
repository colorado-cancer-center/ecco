import type { Unit } from "@/api/index";

/** format map data value */
export function formatValue(
  value: number | string,
  unit?: Unit,
  compact = false,
): string {
  if (typeof value === "string") return value;
  const format: Intl.NumberFormatOptions = {};
  let suffix = "";
  switch (unit) {
    case "percent":
      value *= 100;
      format.maximumFractionDigits = compact ? 1 : 2;
      suffix = "%";
      break;
    case "count":
      format.notation = compact ? "compact" : "standard";
      break;
    case "rate":
      format.maximumSignificantDigits = compact ? 3 : 5;
      break;
    case "dollar_amount":
      format.notation = compact ? "compact" : "standard";
      format.style = "currency";
      format.currency = "USD";
      break;
    case "rank":
      format.maximumSignificantDigits = compact ? 3 : 5;
      break;
    case "ordinal":
      break;
    case "ratio":
      format.maximumFractionDigits = compact ? 2 : 5;
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
