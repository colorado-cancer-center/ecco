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
      description: `
        <div>Welcome to <b>ECCO</b>, an interactive resource for <b>exploring cancer data in Colorado</b>!</div>
        <div><em>This tool is intended to support research, community inquiries, and outreach activities. It should not be used to guide clinical decisions.</em></div>
      `,
    },
  },
  {
    attachTo: { element: "#map-grid" },
    content: {
      title: "Intro",
      description:
        "<div>View map data like population, demographics, cancer burden & disparities, risk factors, health behaviors, and environmental exposures, and local resources like cancer prevention, screening, treatment, and survivorship.</div>",
    },
  },
  {
    attachTo: { element: "#geographic-level" },
    content: { title: "Geographic level", description: "Lorem ipsum" },
  },
  {
    attachTo: { element: "#statistic" },
    content: { title: "Statistic", description: "Lorem ipsum" },
  },
  {
    attachTo: { element: "#locations" },
    content: { title: "Locations", description: "Lorem ipsum" },
  },
  {
    attachTo: { element: "#compare" },
    content: { title: "Compare", description: "Lorem ipsum" },
  },
  {
    attachTo: { element: "#map-controls" },
    content: { title: "Map Controls", description: "Lorem ipsum" },
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
        modifiers: [{ name: 'offset', options: { offset: [16, 16] } }],
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
