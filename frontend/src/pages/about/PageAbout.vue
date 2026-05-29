<template>
  <section>
    <AppHeading level="1">About</AppHeading>

    <p>
      Welcome to <b>ECCO</b>, an interactive resource for
      <b>exploring cancer data in Colorado</b>! View data like population,
      demographics, cancer burden & disparities, risk factors, health behaviors,
      and environmental exposures, and local resources like cancer prevention,
      screening, treatment, and survivorship.
    </p>

    <p> Presented by the University of Colorado Cancer Center</p>
    <AppLink to="https://medschool.cuanschutz.edu/colorado-cancer-center">
      <img
        src="@/assets/logo.png"
        class="h-20"
        alt="University of Colorado Cancer Center"
      />
    </AppLink>
  </section>

  <section>
    <AppHeading level="2">Disclaimer</AppHeading>

    <p>
      This tool is intended to support research, community inquiries, and
      outreach activities. It should not be used to guide clinical decisions.
    </p>
  </section>

  <section>
    <AppHeading level="2">The Map</AppHeading>

    <p>
      Create your own map to visualize your data and region of interest. First
      select the geographic level you want to see data split by, e.g. county or
      tract (census). Then select what type of data statistic you want to see,
      e.g. % college graduates, household income, high rent burden. Note that
      some statistics are only available for certain geographic levels. You can
      select locations to overlay on the map, e.g. screening centers, clinics,
      specialists.
    </p>

    <p>
      You can download the raw data in tabular form to perform analyses and
      produce other tables, charts, etc. You can also download the current view
      of the map as an image.
    </p>
  </section>

  <section>
    <AppHeading level="2">Acknowledge</AppHeading>

    <p>
      If you find this site, software, or data useful in your publications,
      presentations, or other materials, please consider citing it:
    </p>

    <blockquote>
      Lowery JT, Alquaddoomi F, Rubinetti V, Burus T, Jardine C, Warren AC,
      Walsh J, Borrayo E, Davis S.
      <br />
      Exploring Cancer in Colorado using a novel data platform: the ECCO
      experience.
      <br />
      medRxiv (preprint): 2026.02.03.26345489, doi:
      10.64898/2026.02.03.26345489, PMID: 41674638, PMCID: PMC12889761
    </blockquote>

    <p>
      By acknowledging our work, you help support our ongoing efforts to provide
      accurate and up-to-date cancer statistics to the public, researchers, and
      healthcare professionals. It also helps others locate the source of the
      information, promoting transparency and facilitating further research.
    </p>

    <p>
      If you have any questions or require additional information for your
      acknowledgement, please feel free to
      <AppLink to="/contact">contact us</AppLink>. Thank you for your
      cooperation and for using our site.
    </p>

    <p>
      This work is supported by the University of Colorado Cancer Center Support
      Grant (P30CA046934).
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import AppHeading from "@/components/AppHeading.vue";
import AppLink from "@/components/AppLink.vue";
import { appTitle } from "@/meta";

/** page title */
onMounted(() => (appTitle.value = ["About"]));
</script>
