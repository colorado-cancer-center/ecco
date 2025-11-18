/** find next/previous node that matches condition, in dom order */
export const findClosest = (
  element: HTMLElement,
  condition: (element: HTMLElement) => boolean,
  direction: "next" | "previous",
) => {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_ELEMENT,
  );
  walker.currentNode = element;
  while (direction === "next" ? walker.nextNode() : walker.previousNode())
    if (condition(walker.currentNode as HTMLElement))
      return walker.currentNode as HTMLElement;
};
