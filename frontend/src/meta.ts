import { ref, watchEffect } from "vue";

/**
 * from
 * https://github.com/monarch-initiative/monarch-app/blob/main/frontend/src/global/meta.ts
 */

/** project info */
const { VITE_TITLE } = import.meta.env;

/** multi-part page title as array, gets joined with a | separator */
export const appTitle = ref<string[]>([VITE_TITLE]);

/** set metadata value */
const setTag = (property = "", value = "") =>
  document
    .querySelector(`meta[name='${property}'], meta[property='${property}']`)
    ?.setAttribute("content", value);

/** update document title meta tags */
watchEffect(() => {
  const title = appTitle.value
    .concat([VITE_TITLE])
    .filter((part) => part)
    .join(" | ");

  document.title = title || "";
  setTag("title", title);
  setTag("og:title", title);
  setTag("twitter:title", title);
});
