import type { Directive } from "vue";

/** directive that stops all event propagations on an element */
export const stop: Directive<HTMLElement> = {
  mounted: (element) =>
    getEvents(element).forEach((event) =>
      element.addEventListener(event, stopProp),
    ),
  beforeUnmount: (element) =>
    getEvents(element).forEach((event) =>
      element.removeEventListener(event, stopProp),
    ),
};

/** get all event names on an element */
function getEvents(element: Element) {
  const events = [];
  for (const key in element)
    if (key.startsWith("on")) events.push(key.substring(2));
  return events;
}

/** stop propagation of an event */
function stopProp(event: Event) {
  event.stopPropagation();
}
