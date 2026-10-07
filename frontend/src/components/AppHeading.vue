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

const headingElement = useTemplateRef<HTMLHeadingElement>("headingElement");

/** determine link from text content of heading */
const updateLink = () =>
  (link.value = kebabCase(id ?? headingElement.value?.textContent ?? ""));

onMounted(updateLink);
onUpdated(updateLink);
</script>

<template>
  <component :is="tag" :id="link" ref="headingElement">
    <AppLink :to="`#${link}`" class="contents">
      <slot />
    </AppLink>
  </component>
</template>
