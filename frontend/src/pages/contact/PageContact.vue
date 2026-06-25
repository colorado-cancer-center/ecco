<script setup lang="ts">
import { onMounted } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppHeading from "@/components/AppHeading.vue";
import { appTitle } from "@/meta";
import { Bug, Form, Mail } from "@lucide/vue";

/** page title */
onMounted(() => (appTitle.value = ["Contact"]));
</script>

<template>
  <section>
    <AppHeading level="1">Contact</AppHeading>

    <p>
      To suggest a <b>new data</b> source, report an <b>issue</b>, or for
      general <b>questions</b> or <b>help</b>, please reach out to us:
    </p>

    <div class="flex flex-wrap gap-4">
      <AppButton
        to="https://app.smartsheet.com/b/form/e66c076519a34f59a253a9e9e40b9c03"
      >
        <Form />
        Feedback Form
      </AppButton>
      <AppButton
        to="https://github.com/colorado-cancer-center/ecco/issues/new/choose"
      >
        <Bug />
        GitHub
      </AppButton>
      <AppButton to="mailto:coe@cuanschutz.edu">
        <Mail />
        Email
      </AppButton>
    </div>
  </section>
</template>
