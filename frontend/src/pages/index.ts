import { createRouter, createWebHistory } from "vue-router";
import PageAbout from "./PageAbout.vue";
import PageHome from "./PageHome.vue";

export const routes = [
  {
    name: "Home",
    path: "/",
    component: PageHome,
  },
  {
    name: "About",
    path: "/about",
    component: PageAbout,
  },
];

export const history = createWebHistory();

export const router = createRouter({ history, routes });
