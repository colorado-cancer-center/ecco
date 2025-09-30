<template>
  <component :is="tag" :id="link" ref="heading" class="heading">
    <slot />

    <AppLink
      v-if="link"
      :to="'#' + link"
      class="anchor"
      :aria-label="'Link to this section'"
    >
      <font-awesome-icon :icon="faLink" class="icon" />
    </AppLink>
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, onUpdated, ref, useTemplateRef } from "vue";
import { kebabCase } from "lodash";
import { faLink } from "@fortawesome/free-solid-svg-icons";
import AppLink from "@/components/AppLink.vue";

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

<style scoped>
.anchor {
  display: inline-block;
  width: 0;
  margin-left: 0.5em;
  font-size: 0.8em;
  text-decoration: none;
  opacity: 0;
  transition:
    opacity var(--fast),
    color var(--fast);
}

.anchor:focus {
  opacity: 1;
}

.heading:hover .anchor {
  opacity: 1;
}
</style>
