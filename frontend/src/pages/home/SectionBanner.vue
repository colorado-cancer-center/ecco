<template>
  <AppAlert>
    <p>
      Welcome to <b>ECCO</b>! This tool is intended to support research,
      community inquiries, and outreach activities. It should not be used to
      guide clinical decisions.
    </p>
    <div class="buttons">
      <AppButton
        to="https://app.smartsheet.com/b/form/e66c076519a34f59a253a9e9e40b9c03"
        :icon="faComment"
        :flip="true"
        :accent="true"
        >Give us feedback</AppButton
      >
    </div>
  </AppAlert>
</template>

<script setup lang="ts">
import { faComment } from "@fortawesome/free-regular-svg-icons";
import AppAlert from "@/components/AppAlert.vue";
import AppButton from "@/components/AppButton.vue";
</script>
