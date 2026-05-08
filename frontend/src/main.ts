import "tippy.js/dist/tippy.css";
import "./styles.css";
import "@fontsource-variable/inter/wght.css";
import { createApp } from "vue";
import { createGtag } from "vue-gtag";
import VueTippy from "vue-tippy";
import { router } from "@/pages";
import { stop } from "@/stop";
import { tippyOptions } from "@/tooltip";
import App from "./App.vue";

console.debug(import.meta, import.meta.env);

const app = createApp(App);

app.use(router);
app.use(VueTippy, tippyOptions);
app.directive("stop", stop);

if (window.location.hostname === new URL(import.meta.env.VITE_URL).hostname)
  createGtag({ tagId: "G-XESEVBEL2X", pageTracker: { router } });

app.mount("#app");
