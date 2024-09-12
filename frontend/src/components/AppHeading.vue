<template>
  <component :is="tag" :id="link" ref="heading">
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
import { computed, onMounted, onUpdated, ref } from "vue";
import { kebabCase } from "lodash";
import { faLink } from "@fortawesome/free-solid-svg-icons";
import AppLink from "@/components/AppLink.vue";

type Props = {
  /** heading level */
  level: "1" | "2" | "3" | "4";
  /** manually specified id */
  id?: string;
};

const props = defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** hash link of heading */
const link = ref("");

/** tag of heading */
const tag = computed(() => "h" + props.level);

/** heading ref */
const heading = ref<HTMLElement>();

/** determine link from text content of heading */
function updateLink() {
  link.value = kebabCase(props.id ?? heading.value?.textContent ?? "");
}

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

:is(h1, h2, h3, h4):hover .anchor {
  opacity: 1;
}
</style>
