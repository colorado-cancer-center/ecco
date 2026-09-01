<script setup lang="ts">
import type { StepEntity } from "v-onboarding";
import { onMounted, useTemplateRef } from "vue";
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

/** tour handler */
const tour = useTemplateRef("tour");
const { start, finish } = useVOnboarding(tour);

/** tour steps */
const steps: StepEntity[] = [
  {
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
    attachTo: { element: "#map-grid" },
    content: {
      title: "Intro",
      description:
        "View map data like population, demographics, cancer burden & disparities, risk factors, health behaviors, and environmental exposures, and local resources like cancer prevention, screening, treatment, and survivorship.",
    },
  },
  {
    attachTo: { element: "#map-grid" },
    content: {
      title: "Map Controls",
      description:
        "Click and drag to move the map. Scroll/pinch to zoom. Try clicking or hovering over an item for more info.",
    },
  },
  {
    attachTo: { element: "#geographic-level" },
    content: {
      title: "Geographic level",
      description:
        "Select how the map is subdivided from the levels available in our data.",
    },
  },
  {
    attachTo: { element: "#statistic" },
    content: {
      title: "Statistic",
      description:
        'Select the main data to be colored on the map. Search for terms of interest or browse through the categories. Some statistics have extra sub-filtering ("facets") you can select, like female vs. male.',
    },
  },
  {
    attachTo: { element: "#locations" },
    content: {
      title: "Resources",
      description:
        "Choose additional resources, locations, sites, boundaries, and more to overlay on the map.",
    },
  },
  {
    attachTo: { element: "#compare" },
    content: {
      title: "Compare",
      description:
        "Compare multiple maps side by side. Add/select a new map and choose a different set of level/statistic/resources to compare. Drag the mini-maps to reorder, click the Xs to remove.",
    },
  },
  {
    attachTo: { element: "#customizations" },
    content: {
      title: "Customizations",
      description:
        "Advanced. Customize the look and feel of the map, like colors, imagery, scale, etc.",
    },
  },
  {
    attachTo: { element: "#map-download" },
    content: {
      title: "Download",
      description:
        "Download the map in different formats for display or analysis.",
    },
  },
  {
    attachTo: { element: "header" },
    content: {
      title: "Share",
      description:
        "Your level/statistic/resources selections are saved in the URL. You can simply share the URL with someone as you would with any other site. Use your browser's back/forward buttons to quickly hop between or undo selections.",
    },
  },
  {
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

/** remember user preference */
const dismissed = useLocalStorage("tour-dismissed", false);

/** close and remember dismissed preference */
const dismiss = () => {
  dismissed.value = true;
  finish();
};

/** start if not dismissed */
if (!dismissed.value) onMounted(start);

/** exit */
onClickOutside(tour, finish);
useEventListener("keyup", (event: KeyboardEvent) => {
  if (event.key === "Escape") finish();
});
</script>

<template>
  <VOnboardingWrapper
    ref="tour"
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
          <div class="contents" v-html="step.content.description" />
          <div class="flex flex-row-reverse gap-4">
            <button @click="next">
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
</template>

<style scoped>
@reference "@/styles.css";

.step button {
  @apply bg-stone-200 rounded-md px-2 py-1 hover:bg-theme;
}
</style>
