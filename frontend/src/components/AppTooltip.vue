<script setup lang="ts">
import { onMounted, useSlots, useTemplateRef } from "vue";
import { makeLabel } from "@/util/string";
import {
  TooltipArrow,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
} from "reka-ui";

defineOptions({ inheritAttrs: false });

type Props = {
  content?: string;
};

const { content } = defineProps<Props>();

type Slots = {
  default: () => unknown;
  content?: () => unknown;
};

defineSlots<Slots>();

const slots = useSlots();
const trigger = useTemplateRef<{ $el: HTMLElement }>("trigger");

onMounted(() => {
  const element = trigger.value?.$el;
  if (!(element instanceof HTMLElement) || (!content && !slots.content)) return;

  if (window.getComputedStyle(element).cursor === "auto")
    element.style.cursor = "help";

  const text = content ?? element.innerText;
  if (!element.innerText.trim() && text)
    element.setAttribute("aria-label", makeLabel(text));
});
</script>

<template>
  <template v-if="content || $slots.content">
    <TooltipProvider :delay-duration="100" :skip-delay-duration="0">
      <TooltipRoot>
        <TooltipTrigger ref="trigger" v-bind="$attrs" as-child>
          <slot />
        </TooltipTrigger>
        <TooltipPortal>
          <TooltipContent
            :side-offset="16"
            :collision-padding="16"
            :arrow-padding="16"
            class="z-90 rounded-md border border-black bg-white p-2 will-change-transform trim"
          >
            <slot name="content">{{ content }}</slot>
            <TooltipArrow as-child>
              <div
                class="absolute left-1/2 size-3 -translate-1/2 rotate-45 border border-black border-t-white border-l-white bg-white"
              />
            </TooltipArrow>
          </TooltipContent>
        </TooltipPortal>
      </TooltipRoot>
    </TooltipProvider>
  </template>
  <slot v-else />
</template>
