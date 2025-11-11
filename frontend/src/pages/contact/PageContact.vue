<template>
  <section>
    Selected:<br />{{ selected.map((s) => s.id).join(" → ") }}
    <br />
    <br />
    <input v-model="search" placeholder="Search..." />
    <br />
    <br />
    <AppTree v-model="selected" :children="children" :search="search" />
  </section>

  <section>
    <AppHeading level="1">Contact</AppHeading>

    <div class="row">
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
import { ref } from "vue";
import { faGithub } from "@fortawesome/free-brands-svg-icons";
import {
  faComment,
  faQuestionCircle,
} from "@fortawesome/free-regular-svg-icons";
import {
  faBug,
  faDownload,
  faEnvelope,
  faFlask,
} from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppTree from "@/components/AppTree.vue";
import { entries } from "@/util/types";
import data from "./test.json";

const actions = [
  {
    label: "Download",
    icon: faDownload,
    onClick: console.log,
  },
];

const children = entries(data).map(([id, { label, categories }]) => ({
  id,
  label,
  children: entries(categories).map(([id, { label, measures }]) => ({
    id,
    label,
    children: entries(measures).map(([id, { label }]) => ({
      id,
      label,
      actions,
    })),
    actions,
  })),
}));

const selected = ref<{ id: string; label: string }[]>([]);
const search = ref("");
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
