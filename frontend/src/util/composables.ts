import { computed, nextTick, onMounted, ref, shallowRef, watch } from "vue";
import type { Ref } from "vue";
import { debounce, round } from "lodash";
import {
  useMutationObserver,
  useResizeObserver,
  useScroll,
  useUrlSearchParams,
} from "@vueuse/core";

/**
 * reactive variable synced with url params, as object of strings. only supports
 * replace, not push
 */
const params = useUrlSearchParams("history");

/** generic param type */
type Param<T> = {
  parse: (value: string) => T;
  stringify: (value: T) => string;
};

/** param treated as string */
export const stringParam: Param<string> = {
  parse: (value) => value,
  stringify: (value) => String(value),
};

/** param treated as number */
export const numberParam: Param<number> = {
  parse: (value) => Number(value) || 0,
  /** a few decimals good enough for lat/long: */
  /** https://en.wikipedia.org/wiki/Decimal_degrees#Precision */
  stringify: (value) => String(round(value || 0, 5)),
};

/** param treated as boolean */
export const booleanParam: Param<boolean> = {
  parse: (value) => (value.toLowerCase() === "true" ? true : false),
  stringify: (value) => String(value),
};

/** param treated as array of other params */
export const arrayParam = <T>(param: Param<T>): Param<T[]> => ({
  parse: (value) => value.split(",").map(param.parse),
  stringify: (value) => value.map(param.stringify).join(","),
});

/** reactive variable synced with a specific url param */
/** no good third party solution exists for this, so write our own basic version */
/** see https://github.com/vueuse/vueuse/issues/3398 */
export const useUrlParam = <T>(
  name: string,
  { parse, stringify }: Param<T>,
  initialValue: T,
) => {
  /** https://github.com/vuejs/composition-api/issues/483 */
  const variable = shallowRef(initialValue);

  /** when url changes, update variable */
  watch(
    () => params[name],
    () => {
      const param = params[name] || "";
      const value = parse(Array.isArray(param) ? param.join() : param);
      /**
       * stringify process is sometimes "lossy" (e.g. rounding decimal places),
       * so compare values after that process
       */
      if (param === stringify(variable.value)) return;
      if (value) variable.value = value;
    },
    { immediate: true },
  );

  /** when variable changes, update url */
  const updateUrl = debounce(() => {
    const value = stringify(variable.value);
    if (params[name] === value) return;
    if (value) params[name] = value;
    else delete params[name];
  }, 200);
  watch(variable, updateUrl);

  return variable;
};

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
  keep = false,
) => {
  /** query state */
  const status = ref<"" | "loading" | "error" | "success">("");

  /** query results */
  const data = shallowRef<Data>(defaultValue);
  /** https://github.com/vuejs/composition-api/issues/483 */

  /** latest query id, unique to this useQuery instance */
  let latest: Symbol;

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
