<script lang="ts">
export const startEvent = "tour-step-start";
export const endEvent = "tour-step-end";
</script>

<script setup lang="ts">
import type { StepEntity } from "v-onboarding";
import { onMounted, ref, useTemplateRef, watchEffect } from "vue";
import {
  onClickOutside,
  useEventListener,
  useLocalStorage,
} from "@vueuse/core";
import {
  useVOnboarding,
  VOnboardingStep,
  VOnboardingWrapper,
} from "v-onboarding";
import "v-onboarding/dist/style.css";

type Slots = {
  trigger: [{ start: (reset?: boolean) => void }];
};

defineSlots<Slots>();

/** tour handler */
const tourElement = useTemplateRef("tourElement");
const tour = useVOnboarding(tourElement);

/** current step */
const index = useLocalStorage("tour-step", 0);

/** is tour open */
const open = ref(false);

/** common step options */
const common: Partial<StepEntity> = {
  on: {
    beforeStep: (option) => {
      /** track step index */
      index.value = option?.index || 0;

      getElement()?.dispatchEvent(new CustomEvent(startEvent));
    },
    afterStep: () => {
      const element = getElement();
      if (!element) return;
      getElement()?.dispatchEvent(new CustomEvent(endEvent));
    },
  },
};

/** current element */
const getElement = () => {
  const attach = steps[index.value]?.attachTo?.element;
  if (typeof attach === "function") return attach();
  if (typeof attach === "string") return document.querySelector(attach) || null;
  if (!attach) return null;
  return attach.value || null;
};

/** tour steps */
const steps: StepEntity[] = [
  {
    ...common,
    attachTo: { element: "header" },
    content: {
      title: "Welcome",
      description: [
        "<div>Welcome to <b>ECCO</b>, an interactive site for <b>exploring cancer data in Colorado</b>!</div>",
        "<div><em>This tool is intended to support research, community inquiries, and outreach activities. It should not be used to guide clinical decisions.</em></div>",
      ].join(""),
    },
  },
  {
    ...common,
    attachTo: { element: "#map-grid" },
    content: {
      title: "Intro",
      description:
        "View map statistics like population, demographics, cancer burden, risk factors, health behaviors, and environmental exposures, and local resources like cancer prevention, screening, and treatment.",
    },
  },
  {
    ...common,
    attachTo: { element: "#map-grid" },
    content: {
      title: "Map Controls",
      description:
        "Click + drag to move the map. Scroll/pinch to zoom. Click/hover over items for more info.",
    },
  },
  {
    ...common,
    attachTo: { element: "#geographic-level" },
    content: {
      title: "Geographic level",
      description:
        "Select how the map is subdivided from the levels available in our data.",
    },
  },
  {
    ...common,
    attachTo: { element: "#statistic" },
    content: {
      title: "Statistic",
      description:
        'Select the main data to be colored on the map. Search for terms of interest or browse by category. Some statistics have extra sub-filters ("facets") you can select, like female vs. male.',
    },
  },
  {
    ...common,
    attachTo: { element: "#resources" },
    content: {
      title: "Resources",
      description:
        "Overlay local resources on the map – like clinics, centers, and services – and other locations like boundaries and districts.",
    },
  },
  {
    ...common,
    attachTo: { element: "#compare" },
    content: {
      title: "Compare",
      description:
        "Compare multiple maps side by side. Add/select a new map and choose a different combo of level/statistic/resources to compare. Drag the mini-maps to reorder, click the Xs to remove.",
    },
  },
  {
    ...common,
    attachTo: { element: "#customizations" },
    content: {
      title: "Customizations",
      description:
        "Advanced. Customize the look and feel of the map, like colors, imagery, scale, etc.",
    },
  },
  {
    ...common,
    attachTo: { element: "#map-download" },
    content: {
      title: "Download",
      description:
        "Download the map in different formats for display or analysis.",
    },
  },
  {
    ...common,
    attachTo: { element: "header" },
    content: {
      title: "Share",
      description:
        "Your level/statistic/resource selections are saved in the URL. You can simply share your current page with someone as you would any other site. Use your browser's back/forward buttons to quickly hop between or undo selections.",
    },
  },
  {
    ...common,
    attachTo: { element: "nav" },
    content: {
      title: "More Info",
      description: [
        "<div>Find more info on these pages. Reach out to us for help, questions, or feedback!</div>",
        "<div>Try hovering over items on the site for in-place info/help.</div>",
      ].join(""),
    },
  },
];

watchEffect(() => {});

/** remember user preference */
const dismissed = useLocalStorage("tour-dismissed", false);

/** close and remember dismissed preference */
const dismiss = () => {
  open.value = false;
  dismissed.value = true;
  index.value = 0;
  tour.finish();
};

/** start tour */
const start = (reset = false, dismiss = true) => {
  open.value = true;
  let step = index.value;
  if (reset) step = 0;
  tour.start();
  tour.goToStep(step);
  if (dismiss) dismissed.value = false;
};

/** stop tour */
const stop = (reset = false, dismiss = false) => {
  open.value = false;
  tour.finish();
  if (reset) index.value = 0;
  if (dismiss) dismissed.value = true;
};

/** start on page load */
if (!dismissed.value) onMounted(start);

/** exit */
onClickOutside(tourElement, () => stop());
useEventListener("keyup", (event: KeyboardEvent) => {
  if (event.key === "Escape") stop();
});
</script>

<template>
  <VOnboardingWrapper
    ref="tourElement"
    :steps="steps"
    class="[--v-onboarding-step-z:100]"
    :options="{
      popper: {
        placement: 'top',
        modifiers: [
          { name: 'offset', options: { offset: [16, 16], padding: 8 } },
          { name: 'flip', options: { padding: 16 } },
        ],
      },
      overlay: { padding: 8, borderRadius: 8 },
    }"
  >
    <template #default="{ step, next, previous, isFirst, isLast }">
      <VOnboardingStep>
        <div class="step flex max-w-100 flex-col gap-4 rounded-md bg-white p-4">
          <div
            class="text-lg tracking-wide text-stone-500 uppercase"
            v-html="step.content.title"
          />
          <div
            class="contents"
            role="alert"
            v-html="step.content.description"
          />
          <div class="flex flex-row-reverse gap-4">
            <button @click="isLast ? stop(true, true) : next()">
              {{ isLast ? "Finish" : "Next" }}
            </button>
            <button v-if="!isFirst" @click="previous">Back</button>
            <div class="grow" />
            <button @click="dismiss">Dismiss</button>
          </div>
        </div>
      </VOnboardingStep>
    </template>
  </VOnboardingWrapper>
  <slot v-bind="{ start }" name="trigger" />
</template>

<style scoped>
@reference "@/styles.css";

.step button {
  @apply bg-stone-200 rounded-md px-2 py-1 hover:bg-theme;
}
</style>
