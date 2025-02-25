import type { TippyOptions } from "vue-tippy";
import type { Instance } from "tippy.js";
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
    duration: [100, 0],
    delay: [100, 0],
    onCreate: update,
    onShow: update,
    // onHide: () => false,
  },
};

/** create or update tooltip instance */
function update({ reference, props: { content } }: Instance) {
  /** don't show if content blank */
  if (!content) return false;

  if (
    (reference instanceof HTMLElement || reference instanceof SVGElement) &&
    window.getComputedStyle(reference).cursor === "auto"
  )
    reference.style.cursor = "help";

  /** set aria label to content */
  if (
    (reference instanceof HTMLElement && !reference.innerText.trim()) ||
    reference instanceof SVGElement
  )
    reference.setAttribute("aria-label", makeLabel(String(content)));
}
