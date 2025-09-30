/** make plain text label from (possible) html string */
export const makeLabel = (string: string) =>
  (
    new DOMParser().parseFromString(string, "text/html").body.textContent || ""
  ).replaceAll(/\s+/g, " ");
