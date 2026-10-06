import type { Ref } from "vue";
import { ref, watchEffect } from "vue";
import { frame, sleep } from "@/util/misc";

/**
 * inspired by tanstack-query. simple query manager/wrapper for making queries
 * in components. reduces repetitive boilerplate code for loading/error states,
 * try/catch blocks, de-duplicating requests, etc.
 */
export const useQuery = <Data, Args extends unknown[]>(
  /**
   * main async func that returns data. should be side-effect free to avoid race
   * conditions, because multiple can be running at same time.
   */
  func: (...args: Args) => Promise<Data>,
  /** default value used for data before done loading and on error. */
  defaultValue: Data,
  /** whether we should keep previous data while loading new data */
  keep = true,
) => {
  /** query state */
  const status = ref<"" | "loading" | "error" | "success">("");

  /** query results */
  const data = ref<Data>(defaultValue);

  /** latest query id, unique to this useQuery instance */
  let latest: symbol;

  /** wrapped query function */
  const query = async (...args: Args): Promise<void> => {
    /** unique id for current run */
    const current = Symbol();
    latest = current;

    /** check if this run is still latest */
    const isLatest = () =>
      current === latest ? true : console.warn("Stale query");

    try {
      /** reset state */
      status.value = "loading";
      if (!keep) data.value = defaultValue;

      /** run provided function */
      const result = await func(...args);

      if (isLatest()) {
        /** assign results to data */
        data.value = result;
        status.value = "success";
      }
    } catch (error) {
      if (isLatest()) {
        console.error(error);
        status.value = "error";
      }
    }
  };

  return { query, data, status };
};

/** control expanding/collapsing height of element with transition */
export const useAutoHeight = (
  ref: Ref<HTMLElement | null>,
  open: Ref<boolean>,
) => {
  let first = true;
  watchEffect((onCleanup) => {
    const element = ref.value;
    if (!element) return;

    /** reset height so content can size naturally */
    const reset = () => (element.style.maxHeight = "");

    /** don't transition on first render */
    if (first) {
      element.style.transition = "none";
      sleep().then(() => (element.style.transition = ""));
      first = false;
    }

    if (open.value) {
      /** set height to content height */
      element.style.maxHeight = element.scrollHeight + "px";
      /** reset after transition */
      element.addEventListener("transitionend", reset, { once: true });
    } else {
      /** set starting height */
      element.style.maxHeight = element.scrollHeight + "px";
      frame().then(() => {
        /** collapse */
        element.style.maxHeight = "0px";
      });
    }

    onCleanup(() => {
      element.removeEventListener("transitionend", reset);
    });
  });
};
