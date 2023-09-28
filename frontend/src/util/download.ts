/** download blob as file */
export function download(
  data: BlobPart,
  filename: string | string[],
  type: string,
) {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = [filename]
    .flat()
    .join("_")
    .replaceAll(/[^ A-Za-z0-9_-]/g, " ")
    .replaceAll(/\s+/g, "-");
  link.click();
  window.URL.revokeObjectURL(url);
}

/** download blob as png */
export function downloadPng(data: BlobPart, filename: string | string[]) {
  download(data, filename, "image/png");
}
