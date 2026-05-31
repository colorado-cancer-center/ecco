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

/** wait for func to return stable value */
export const waitForStable = async <Return>(
  func: () => Return,
  /** wait until func returns same value for at least this long */
  wait = 200,
  /** check value every this many ms */
  interval = 10,
  /** hard time limit */
  max = 3000,
): Promise<Return | undefined> => {
  let lastChanged = now();
  let prevResult: Return | undefined;
  for (let tries = max / interval; tries > 0; tries--) {
    const result = func();
    if (result !== prevResult) lastChanged = now();
    prevResult = result;
    if (result !== undefined && now() - lastChanged > wait) return result;
    await sleep(interval);
  }
};

/** copy text to clipboard */
export const copy = async (text: string) => {
  await navigator.clipboard.writeText(text);
  window.alert("Copied to clipboard");
};
