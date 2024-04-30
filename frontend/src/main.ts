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

createApp(App)
  .component("font-awesome-icon", FontAwesomeIcon)
  .use(router)
  .use(
    VueGtag,
    {
      config: { id: "G-XESEVBEL2X" },
      enabled: window.location.hostname === "ecco.cu-dbmi.dev",
    },
    router,
  )
  .use(VueTippy, tippyOptions)
  .directive("stop", stop)
  .mount("#app");
