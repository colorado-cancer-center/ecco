import { createApp } from "vue";
import VueTippy from "vue-tippy";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { router } from "@/views";
import App from "./App.vue";
import "tippy.js/dist/tippy.css";
import { tippyOptions } from "@/tooltip";
import "./styles.css";

createApp(App)
  .component("font-awesome-icon", FontAwesomeIcon)
  .use(router)
  .use(VueTippy, tippyOptions)
  .mount("#app");
