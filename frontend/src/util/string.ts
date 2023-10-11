/** make plain text label from (possible) html string */
export function makeLabel(string: string) {
  return (
    new DOMParser().parseFromString(string, "text/html").body.textContent || ""
  ).replaceAll(/\s+/g, " ");
}
