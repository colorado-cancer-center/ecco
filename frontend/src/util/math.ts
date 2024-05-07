/** format map data value */
export function formatValue(
  value: number,
  percent = true,
  compact = true,
): string {
  if (percent)
    return (
      (value * 100).toLocaleString(undefined, {
        maximumSignificantDigits: compact ? 3 : 5,
      }) + "%"
    );
  else
    return value.toLocaleString(
      undefined,
      compact
        ? {
            notation: "compact",
            maximumSignificantDigits: 3,
          }
        : undefined,
    );
}

/** check if min/max is within small range and should be treated as percent */
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
