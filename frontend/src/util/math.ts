import { round } from "lodash";

/** format map data value */
export function formatValue(
  value?: number,
  min?: number,
  max?: number,
  compact = true,
): string {
  if (value === undefined || min === undefined || max === undefined) return "-";
  /** if all values between 0 and 1, value represents percentage */
  if (min >= 0 && max <= 1) return round(value * 100, compact ? 1 : 3) + "%";
  /** otherwise, format as regular number */ else
    return value.toLocaleString(undefined, {
      notation: compact ? "compact" : undefined,
      maximumFractionDigits: Math.abs(value) < 1 ? 2 : undefined,
    });
}

/** normalize value from [min, max] to [0, 1], apply math function to value,
 * then un-normalize */
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
