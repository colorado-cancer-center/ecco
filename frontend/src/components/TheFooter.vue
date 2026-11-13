<script setup lang="ts">
import { useTemplateRef, watchEffect } from "vue";
import AppLink from "@/components/AppLink.vue";
import { useElementBounding } from "@vueuse/core";
import { clamp } from "lodash";

const footerElement = useTemplateRef("footerElement");
const size = useElementBounding(footerElement);

/** track footer size */
watchEffect(() => {
  const top = clamp(size.top.value, 0, window.innerHeight);
  const bottom = clamp(size.bottom.value, 0, window.innerHeight);
  /** amount of footer height visible in viewport */
  const height = bottom - top;
  document.documentElement.style.setProperty("--footer-height", `${height}px`);
});
</script>

<template>
  <footer
    ref="footerElement"
    class="flex items-center justify-end gap-4 p-4 max-sm:flex-col"
  >
    <span class="flex flex-wrap justify-center gap-4">
      <AppLink to="https://github.com/colorado-cancer-center/ecco">
        Source Code
      </AppLink>
      <AppLink
        to="https://github.com/colorado-cancer-center/ecco/blob/main/LICENSE"
      >
        License
      </AppLink>
    </span>
  </footer>
</template>
