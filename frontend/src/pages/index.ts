import { createRouter, createWebHistory } from "vue-router";
import PageContact from "@/pages/contact/PageContact.vue";
import PageCounty from "@/pages/county/PageCounty.vue";
import PageSources from "@/pages/sources/PageSources.vue";
import { sleep, waitFor } from "@/util/misc";
import PageAbout from "./about/PageAbout.vue";
import PageHome from "./home/PageHome.vue";

export const routes = [
  {
    name: "Home",
    path: "/",
    component: PageHome,
    beforeEnter: () => {
      const url = window.sessionStorage.redirect as string;
      if (url) {
        console.debug("Redirecting to:", url);
        window.sessionStorage.removeItem("redirect");
        return url;
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
