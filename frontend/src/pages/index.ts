import { ref, watch } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import PageContact from "@/pages/contact/PageContact.vue";
// import PageCounty from "@/pages/county/PageCounty.vue";
import PageSources from "@/pages/sources/PageSources.vue";
import { sleep, waitFor } from "@/util/misc";
import { useRouteQuery } from "@vueuse/router";
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
        console.debug("Redirecting to:", redirect);
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
  // {
  //   name: "County",
  //   path: "/county/:id",
  //   component: PageCounty,
  // },
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

/** "commit" tab history entry */
const push = debounce((path: string) => {
  const to = router.resolve(path);
  router.push({ ...to, force: true });
  justPushed = true;
}, 1000);

/** on route change */
router.afterEach((to, from) => {
  if (to.fullPath === from.fullPath) return;
  if (justPushed) return (justPushed = false);
  push(to.fullPath);
});

/** flag to prevent infinite loop */
let justPushed = false;

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
type Param<T> = {
  get: (value: string) => T;
  set: (value: T) => string;
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
export const arrayParam = <T>(param: Param<T>): Param<T[]> => ({
  get: (value) => value.split(",").map(param.get),
  set: (value) => value.map(param.set).join(","),
});

/**
 * work-around for useRouteQuery not support deep reactivity
 * https://github.com/vueuse/vueuse/issues/5200
 */
export const useDeepRouteQuery = <Type>(key: string, initial: Type) => {
  const raw = useRouteQuery(key, JSON.stringify(initial));
  const state = ref(initial);

  let fromRoute = false;

  watch(
    raw,
    (value) => {
      fromRoute = true;
      try {
        state.value = value ? JSON.parse(value) : initial;
      } catch {
        state.value = initial;
      } finally {
        fromRoute = false;
      }
    },
    { immediate: true },
  );

  watch(
    state,
    (value) => {
      if (fromRoute) return;
      const next = JSON.stringify(value);
      if (raw.value !== next) raw.value = next;
    },
    { deep: true },
  );

  return state;
};
