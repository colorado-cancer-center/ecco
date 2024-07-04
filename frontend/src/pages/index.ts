import { createRouter, createWebHistory } from "vue-router";
import PageContact from "@/pages/PageContact.vue";
import PageSources from "@/pages/PageSources.vue";
import { waitFor } from "@/util/misc";
import PageAbout from "./PageAbout.vue";
import PageHome from "./PageHome.vue";

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
  },
  {
    name: "Sources",
    path: "/sources",
    component: PageSources,
  },
  {
    name: "About",
    path: "/about",
    component: PageAbout,
  },
  {
    name: "Contact",
    path: "/Contact",
    component: PageContact,
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
  if (to.hash)
    (await waitFor(to.hash))?.scrollIntoView({
      block: "start",
      behavior: "smooth",
    });
});
