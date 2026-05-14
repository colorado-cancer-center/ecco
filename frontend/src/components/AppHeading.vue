<template>
  <component :is="tag" :id="link" ref="heading">
    <AppLink :to="link" class="contents">
      <slot />
    </AppLink>
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, onUpdated, ref, useTemplateRef } from "vue";
import AppLink from "@/components/AppLink.vue";
import { kebabCase } from "lodash";

type Props = {
  /** heading level */
  level: "1" | "2" | "3" | "4";
  /** manually specified id */
  id?: string;
};

const { level, id } = defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** hash link of heading */
const link = ref("");

/** tag of heading */
const tag = computed(() => "h" + level);

/** heading ref */
const heading = useTemplateRef<HTMLHeadingElement>("heading");

/** determine link from text content of heading */
const updateLink = () =>
  (link.value = kebabCase(id ?? heading.value?.textContent ?? ""));

onMounted(updateLink);
onUpdated(updateLink);
</script>
