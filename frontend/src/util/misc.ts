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

/** wait for element matching selector to appear, checking periodically */
export const waitFor = async <El extends Element>(
  selector: string,
): Promise<El | undefined> => {
  const waits = [
    0, 1, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000,
  ];
  while (waits.length) {
    const match = document.querySelector<El>(selector);
    if (match) return match;
    await sleep(waits.shift());
  }
};
