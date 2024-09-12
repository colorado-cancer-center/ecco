/** make plain text label from (possible) html string */
export function makeLabel(string: string) {
  return (
    new DOMParser().parseFromString(string, "text/html").body.textContent || ""
  ).replaceAll(/\s+/g, " ");
}

/** (lodash's capitalize forces subsequent letters to lowercase) */
export function capitalize(string: string) {
  return string.substring(0, 1).toUpperCase() + string.substring(1);
}
