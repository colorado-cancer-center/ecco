import { createRouter, createWebHistory } from "vue-router";
import PageSources from "@/pages/PageSources.vue";
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
    name: "About",
    path: "/about",
    component: PageAbout,
  },
  {
    name: "Sources",
    path: "/sources",
    component: PageSources,
  },
];

export const history = createWebHistory();

export const router = createRouter({ history, routes });
