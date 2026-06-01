const now = () => window.performance.now();

/** wait ms */
export const sleep = (ms = 0) =>
  new Promise((resolve) => window.setTimeout(resolve, ms));

/** wait for repaint */
export const frame = () =>
  new Promise((resolve) => window.requestAnimationFrame(resolve));

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

/** copy text to clipboard */
export const copy = async (text: string) => {
  await navigator.clipboard.writeText(text);
  window.alert("Copied to clipboard");
};
