import type { TippyOptions } from "vue-tippy";
import { type Instance } from "tippy.js";
import { makeLabel } from "@/util/string";

export const tippyOptions: {
  [key: string]: unknown;
  defaultProps: TippyOptions;
} = {
  directive: "tooltip",
  component: "tooltip",
  defaultProps: {
    allowHTML: true,
    offset: [0, 15],
    delay: 300,
    onCreate: update,
    onShow: update,
    // onHide: () => false,
  },
};

// create or update tooltip instance
function update({ reference, props: { content }, setProps }: Instance) {
  // don't show if content blank
  if (!content) return false;

  setProps({
    // only make interactive if content includes link to click on
    interactive: String(content).includes("<a"),
  });

  // set aria label to content
  reference.setAttribute("aria-label", makeLabel(String(content)));
}
