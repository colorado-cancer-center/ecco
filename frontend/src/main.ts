import { createApp } from "vue";
import { createGtag } from "vue-gtag";
import VueTippy from "vue-tippy";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { router } from "@/pages";
import { stop } from "@/stop";
import { tippyOptions } from "@/tooltip";
import App from "./App.vue";
import "tippy.js/dist/tippy.css";
import "./styles.css";

console.debug(import.meta, import.meta.env);

const app = createApp(App);

app.component("FontAwesomeIcon", FontAwesomeIcon);

app.use(router);
app.use(VueTippy, tippyOptions);
app.directive("stop", stop);

if (window.location.hostname === new URL(import.meta.env.VITE_URL).hostname)
  app.use(createGtag({ tagId: "G-XESEVBEL2X", pageTracker: { router } }));

app.mount("#app");
