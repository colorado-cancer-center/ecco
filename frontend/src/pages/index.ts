import { reactive, ref, watch } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import PageContact from "@/pages/contact/PageContact.vue";
import PageCounty from "@/pages/county/PageCounty.vue";
import PageSources from "@/pages/sources/PageSources.vue";
import { sleep, waitFor } from "@/util/misc";
import { debounce, round } from "lodash";
import PageAbout from "./about/PageAbout.vue";
import PageHome from "./home/PageHome.vue";

/** load redirect storage item */
const redirect = window.sessionStorage.redirect || "";

/** clear redirect storage item right after consuming */
window.sessionStorage.removeItem("redirect");

export const routes = [
  {
    name: "Home",
    path: "/",
    component: PageHome,
    beforeEnter: () => {
      if (redirect) {
        return redirect;
      }
    },
    meta: { header: true },
  },
  {
    name: "Sources",
    path: "/sources",
    component: PageSources,
    meta: { header: true },
  },
  {
    name: "About",
    path: "/about",
    component: PageAbout,
    meta: { header: true },
  },
  {
    name: "Contact",
    path: "/contact",
    component: PageContact,
    meta: { header: true },
  },
  {
    name: "County",
    path: "/county/:id",
    component: PageCounty,
  },
];

export const history = createWebHistory();

export const router = createRouter({
  history,
  routes,
  scrollBehavior: (to, from, savedPosition) => {
    if (savedPosition) return savedPosition;
    else return { top: 0 };
  },
});

router.afterEach(async (to) => {
  /** scroll to hash target */
  if (to.hash) {
    /** wait for target to appear */
    const target = await waitFor(() => document.querySelector(to.hash));
    /** wait for layout shifts */
    await sleep(100);
    /** scroll */
    target?.scrollIntoView({
      block: "start",
      behavior: "smooth",
    });
  }
});

/** generic param type */
type Param<Type> = {
  get: (value: string) => Type;
  set: (value: Type) => string;
};

/** param treated as string */
export const stringParam: Param<string> = {
  get: (value) => value,
  set: (value) => String(value),
};

/** param treated as number */
export const numberParam: Param<number> = {
  get: (value) => Number(value) || 0,
  /** a few decimals good enough for lat/long: */
  /** https://en.wikipedia.org/wiki/Decimal_degrees#Precision */
  set: (value) => String(round(value || 0, 5)),
};

/** param treated as boolean */
export const booleanParam: Param<boolean> = {
  get: (value) => (value.toLowerCase() === "true" ? true : false),
  set: (value) => String(value),
};

/** param treated as array of other params */
export const arrayParam = <Type>(param: Param<Type>): Param<Type[]> => ({
  get: (value) => value.split(",").map(param.get),
  set: (value) => value.map(param.set).join(","),
});

/** param treated as json */
export const jsonParam = <Type>(defaultValue: Type): Param<Type> => ({
  get: (value) => (value ? JSON.parse(value) : defaultValue),
  set: (value) => JSON.stringify(value),
});

/** reactive variable synced with specific url param */
export const useParam = <Type>(
  key: string,
  initialValue: Type,
  { get, set }: Param<Type>,
) => {
  /** reactive variable */
  const value = ref<Type>(
    key in params && params[key] !== undefined
      ? get(params[key])
      : initialValue,
  );

  /** when variable changes */
  watch(
    value,
    () => {
      /** update params */
      const newValue = set(value.value);
      if (params[key] === newValue) return;
      params[key] = newValue;
    },
    { deep: true },
  );

  /** when params change */
  watch(
    () => params[key],
    () => {
      /** update variable */
      if (!(key in params) || params[key] === undefined) return;
      const newValue = get(params[key]);
      if (value.value === newValue) return;
      value.value = newValue;
    },
    { immediate: true },
  );

  return value;
};

/** variable synced with url params */
const params = reactive<Record<string, string>>({});

/** update address bar from local variable */
watch(
  params,
  debounce(() => {
    if (!justUpdated) router.push({ query: params });
  }, 1000),
  { deep: true },
);

let justUpdated = true;

/** update local variable from address bar */
const urlToVar = () => {
  justUpdated = true;
  const url = new URLSearchParams(window.location.search);
  for (const [key, value] of url.entries()) {
    const currentValue = params[key];
    const newValue = String(value);
    if (currentValue !== newValue) params[key] = newValue;
  }
  sleep().then(() => (justUpdated = false));
};
window.addEventListener("popstate", urlToVar);
window.addEventListener("load", urlToVar);
