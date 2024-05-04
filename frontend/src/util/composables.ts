import {
  computed,
  nextTick,
  onMounted,
  shallowRef,
  watch,
  watchEffect,
  type Ref,
} from "vue";
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
export function useUrlParam<T>(
  name: string,
  { parse, stringify }: Param<T>,
  initialValue: T,
) {
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
}

/** style element with gradients at edges to indicate scroll-ability */
export function useScrollable(
  element: Ref<HTMLElement | undefined>,
  thickness = "100px",
) {
  const { arrivedState } = useScroll(element);

  /** whether any scrolling is possible */
  const scrollable = computed(() => {
    const { left, top, right, bottom } = arrivedState;
    return !left || !top || !right || !bottom;
  });

  /** add gradient styles */
  watchEffect(() => {
    if (
      !element.value ||
      window.getComputedStyle(element.value).overflow === "visible"
    )
      return;

    /** whether at edges of element */
    const { left, top, right, bottom } = arrivedState;

    /** generate gradient in direction */
    const grad = (dir: string) =>
      `linear-gradient(to ${dir}, transparent 0, black ${thickness})`;

    /** combine masks into single definition */
    const mask = [
      !left && grad("right"),
      !top && grad("bottom"),
      !right && grad("left"),
      !bottom && grad("top"),
    ]
      .filter(Boolean)
      .join(",");

    /** stack masks */
    element.value.style.webkitMaskComposite = "destination-in";
    element.value.style.maskComposite = "intersect";

    /** set masks */
    element.value.style.webkitMaskImage = mask;
    element.value.style.maskImage = mask;
  });

  /** force scroll to update */
  async function update() {
    await nextTick();
    element.value?.dispatchEvent(new Event("scroll"));
  }
  /** update scroll on some events that might affect element's scrollWidth/Height */
  onMounted(update);
  useResizeObserver(element, update);
  useMutationObserver(element, update, { childList: true, subtree: true });

  return scrollable;
}
