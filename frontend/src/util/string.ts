/** make plain text label from (possible) html string */
export const makeLabel = (string: string) =>
  (
    new DOMParser().parseFromString(string, "text/html").body.textContent || ""
  ).replaceAll(/\s+/g, " ");

/** format date to string */
export const formatDate = (date?: Date | string) => {
  date = date ? new Date(date) : new Date();
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
