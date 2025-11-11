import * as d3 from "d3";

/** wait ms */
export const sleep = (ms = 0) =>
  new Promise((resolve) => window.setTimeout(resolve, ms));

/** wait for repaint */
export const frame = () =>
  new Promise((resolve) => window.requestAnimationFrame(resolve));

/** safe get bbox */
export const getBbox = (selector: string): DOMRect =>
  document.querySelector(selector)?.getBoundingClientRect() ||
  new DOMRect(0, 0, 1, 1);

/** wait for function to return something, checking periodically */
export const waitFor = async <Result>(
  func: () => Result,
): Promise<Result | undefined> => {
  const waits = [
    0, 1, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000,
  ];
  while (waits.length) {
    const result = func();
    if (result) return result;
    await sleep(waits.shift());
  }
};

/** get defined css variable value */
export const getCssVar = (
  name: `--${string}`,
  element = document.documentElement,
) => getComputedStyle(element).getPropertyValue(name);

/** force color to hex format */
export const forceHex = (color: string) =>
  d3.color(color)?.formatHex() || "#000000";

/** convert [0,1] value to two hex digits */
export const toHex = (value = 0) =>
  Math.floor(value * 255)
    .toString(16)
    .padStart(2, "0");

/** copy text to clipboard */
export const copy = async (text: string) => {
  await navigator.clipboard.writeText(text);
  window.alert("Copied to clipboard");
};
