<script setup lang="ts">
import AppButton from "@/components/AppButton.vue";
import SectionMap from "@/pages/home/SectionMap.vue";
import TheTour from "@/pages/home/TheTour.vue";
import { GraduationCap } from "@lucide/vue";
</script>

<template>
  <section class="[--content:999]">
    <SectionMap />
  </section>
  <section>
    <TheTour>
      <template #trigger="{ start }">
        <AppButton class="self-center" @click="start()">
          <GraduationCap />
          Tour this page
        </AppButton>
      </template>
    </TheTour>
  </section>
</template>
