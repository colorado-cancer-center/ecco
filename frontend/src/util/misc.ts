/** wait ms */
export function sleep(ms = 0) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

/** wait for repaint */
export function frame() {
  return new Promise((resolve) => window.requestAnimationFrame(resolve));
}

/** safe get bbox */
export function getBbox(selector: string): DOMRect {
  return (
    document.querySelector(selector)?.getBoundingClientRect() ||
    new DOMRect(0, 0, 1, 1)
  );
}
