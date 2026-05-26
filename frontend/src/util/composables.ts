import type { Ref } from "vue";
import { computed, nextTick, onMounted, ref, watchEffect } from "vue";
import { frame } from "@/util/misc";
import {
  useMutationObserver,
  useResizeObserver,
  useScroll,
} from "@vueuse/core";

/** style element with gradients at edges to indicate scroll-ability */
export const useScrollable = (element: Ref<HTMLElement | undefined>) => {
  const { arrivedState } = useScroll(element);

  /** whether any scrolling is possible */
  const scrollable = computed(() => {
    const { left, top, right, bottom } = arrivedState;
    return !left || !top || !right || !bottom;
  });

  /** force scroll to update */
  const update = async () => {
    await nextTick();
    element.value?.dispatchEvent(new Event("scroll"));
  };
  /** update scroll on some events that might affect element's scrollWidth/Height */
  onMounted(update);
  useResizeObserver(element, update);
  useMutationObserver(element, update, { childList: true, subtree: true });

  return scrollable;
};

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
  watchEffect((onCleanup) => {
    const element = ref.value;
    if (!element) return;

    /** reset height so content can size naturally */
    const reset = () => (element.style.maxHeight = "");

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
