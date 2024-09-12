<template>
  <section>
    <AppHeading level="1">About</AppHeading>

    <AppHeading level="2">The Map</AppHeading>

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

    <AppHeading level="2">Acknowledge</AppHeading>

    <p>
      If you find this site useful in your academic or research work, we ask
      that you acknowledge it as a source in your publications, presentations,
      or other materials. Suggested acknowledgement:
    </p>

    <blockquote>
      Cancer statistics and information were obtained from ECCO ({{ url }}),
      accessed on [DATE], and supported by the University of Colorado Cancer
      Center Support Grant (P30CA046934).
    </blockquote>

    <p>
      By acknowledging our site, you help support our ongoing efforts to provide
      accurate and up-to-date cancer statistics to the public, researchers, and
      healthcare professionals. Your acknowledgement also helps others locate
      the source of the information, promoting transparency and facilitating
      further research.
    </p>

    <p>
      If you have any questions or require additional information for your
      acknowledgement, please feel free to
      <AppLink to="/contact">contact us</AppLink>. Thank you for your
      cooperation and for using our site.
    </p>
  </section>
</template>

<script setup lang="ts">
import AppHeading from "@/components/AppHeading.vue";
import AppLink from "@/components/AppLink.vue";

const { VITE_URL: url } = import.meta.env;
</script>
