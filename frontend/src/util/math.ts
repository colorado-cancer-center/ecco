import { round } from "lodash";

/** format map data value */
export function formatValue(
  value: number,
  percent = true,
  compact = true,
): string {
  if (percent) return round(value * 100, compact ? 1 : 3) + "%";
  else
    return value.toLocaleString(undefined, {
      notation: compact ? "compact" : undefined,
      maximumFractionDigits: Math.abs(value) < 1 ? 2 : undefined,
    });
}

/** check if range is within 0-1 and should be treated as percent */
export function isPercent(min: number, max: number) {
  return min >= 0 && max <= 1;
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
