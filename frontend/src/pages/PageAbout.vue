<template>
  <section>
    <h2>About</h2>

    <h3>The map</h3>

    <p>
      Create your own map to visualize your data and region of interest. First
      select the geographic level you want to see data split by, e.g. county or
      tract (census). Then select what type of data measure you want to see,
      e.g. % college graduates, household income, high rent burden. Note that
      some measures are only available for certain geographic levels. You can
      select locations to overlay on the map, e.g. screening centers, clinics,
      specialists. Click on a region or point on the map to see more details.
    </p>

    <p>
      You can download the raw data in tabular form to perform analyses and
      produce other tables, charts, etc. You can also download the current view
      of the map as an image.
    </p>

    <h3>Contact</h3>

    <p>
      To suggest a new data source, report an issue, or for general questions or
      help, please contact us:
    </p>

    <p class="actions">
      <AppButton
        :icon="faGithub"
        to="https://github.com/colorado-cancer-center/COCancerScope/issues/new/choose"
        >GitHub (preferred)</AppButton
      >
      <AppButton :icon="faEnvelope" to="mailto:jan.lowery@cuanschutz.edu"
        >Email</AppButton
      >
    </p>
  </section>
</template>

<script setup lang="ts">
import { faGithub } from "@fortawesome/free-brands-svg-icons";
import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
</script>
