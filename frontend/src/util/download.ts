type Filename = string | string[];

/** download blob as file */
export const download = (data: BlobPart, filename: Filename, type: string) => {
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
};

/** download blob as png */
export const downloadPng = (data: BlobPart, filename: Filename) =>
  download(data, filename, "image/png");

/** download string as file */
export const downloadString = (data: string, filename: Filename) =>
  download(data, filename, "text/plain");
