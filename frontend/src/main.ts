import { createApp } from "vue";
import VueTippy, { type TippyOptions } from "vue-tippy";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { router } from "@/views";
import App from "./App.vue";
import "tippy.js/dist/tippy.css";
import "./styles.css";

const tippyOptions: { [key: string]: unknown; defaultProps: TippyOptions } = {
  directive: "tooltip",
  component: "tooltip",
  defaultProps: {
    allowHTML: true,
    offset: [0, 15],
    delay: 300,
    // onHide: () => false,
  },
};

createApp(App)
  .component("font-awesome-icon", FontAwesomeIcon)
  .use(router)
  .use(VueTippy, tippyOptions)
  .mount("#app");
