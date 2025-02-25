import { createApp } from "vue";
import VueGtag from "vue-gtag";
import VueTippy from "vue-tippy";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { router } from "@/pages";
import { stop } from "@/stop";
import { tippyOptions } from "@/tooltip";
import App from "./App.vue";
import "tippy.js/dist/tippy.css";
import "./styles.css";

console.debug(import.meta);

const app = createApp(App);

app.component("font-awesome-icon", FontAwesomeIcon);

app.use(router);
app.use(VueTippy, tippyOptions);
app.directive("stop", stop);

app.use(
  VueGtag,
  {
    config: { id: "G-XESEVBEL2X" },
    enabled:
      window.location.hostname === new URL(import.meta.env.VITE_URL).hostname,
  },
  router,
);

app.mount("#app");
