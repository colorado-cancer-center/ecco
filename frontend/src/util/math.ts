import { round } from "lodash";

// format map data value
export function formatValue(value = 0, min = 0, max = 1): string {
  if (min >= 0 && max <= 1) return round(value * 100, 1) + "%";
  else return value.toLocaleString(undefined, { notation: "compact" });
}
