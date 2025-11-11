/** find next/previous node that matches selector, in dom order */
export const findClosest = (
  element: HTMLElement,
  selector: string,
  direction: "next" | "previous",
) => {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_ELEMENT,
  );
  walker.currentNode = element;
  while (direction === "next" ? walker.nextNode() : walker.previousNode())
    if ((walker.currentNode as HTMLElement).matches(selector))
      return walker.currentNode as HTMLElement;
};
