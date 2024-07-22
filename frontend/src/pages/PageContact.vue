<template>
  <section>
    <AppHeading level="2">Contact</AppHeading>

    <div class="buttons">
      <AppButton
        :icon="faComment"
        to="https://app.smartsheet.com/b/form/e66c076519a34f59a253a9e9e40b9c03"
        >Feedback form</AppButton
      >
      <AppButton
        :icon="faGithub"
        to="https://github.com/colorado-cancer-center/ecco/issues/new/choose"
        >GitHub</AppButton
      >
      <AppButton :icon="faEnvelope" to="mailto:coe@cuanschutz.edu"
        >Email</AppButton
      >
    </div>

    <div class="mini-table table">
      <font-awesome-icon :icon="faFlask" />
      <div>Suggest a <b>new data</b> source</div>
      <font-awesome-icon :icon="faBug" />
      <div>Report an <b>issue</b></div>
      <font-awesome-icon :icon="faQuestionCircle" />
      <div>General <b>questions</b> or <b>help</b></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { faGithub } from "@fortawesome/free-brands-svg-icons";
import {
  faComment,
  faQuestionCircle,
} from "@fortawesome/free-regular-svg-icons";
import { faBug, faEnvelope, faFlask } from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
import AppHeading from "@/components/AppHeading.vue";
</script>

<style scoped>
.table {
  place-content: center;
  margin: 40px auto;
  gap: 15px;
}

.table > svg {
  color: var(--dark-gray);
}
</style>
