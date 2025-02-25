import * as d3 from "d3";

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

/** wait for function to return something, checking periodically */
export async function waitFor<Result>(
  func: () => Result,
): Promise<Result | undefined> {
  const waits = [
    0, 1, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000,
  ];
  while (waits.length) {
    const result = func();
    if (result) return result;
    await sleep(waits.shift());
  }
}

/** get defined css variable value */
export const getCssVar = (
  name: `--${string}`,
  element = document.documentElement,
) => getComputedStyle(element).getPropertyValue(name);

/** force color to hex format */
export function forceHex(color: string) {
  return d3.color(color)?.formatHex() || "#000000";
}

/** convert [0,1] value to two hex digits */
export function toHex(value = 0) {
  return Math.floor(value * 255)
    .toString(16)
    .padStart(2, "0");
}
