<template>
  <section>
    <AppHeading level="1">Sources</AppHeading>

    <p>
      Data for ECCO are gathered automatically and periodically from several
      publicly available sources. Dates given below will change over time, and
      should represent the most currently available data and reflect what is
      found on
      <AppLink to="https://cancerinfocus.org/"
        >Cancer InFocus: Catchment Areas</AppLink
      >.
    </p>

    <p class="center">
      <AppButton
        v-tooltip="'Download all sources data in CSV format'"
        :icon="faTable"
        :to="getDownloadAll()"
        :accent="true"
      >
        Download All Data
      </AppButton>
    </p>
  </section>

  <section>
    <AppHeading level="2">Summary</AppHeading>

    <AppStatus v-if="sourcesStatus == 'error'" status="error" />
    <AppStatus v-else-if="sourcesStatus == 'loading'" status="loading" />

    <div v-else-if="sources" class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Data</th>
            <th>Date(s)</th>
            <th>Date Description</th>
            <th>Cite</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(source, index) in sources" :key="index">
            <td>
              <AppLink :to="`#${kebabCase(source.id)}`">
                {{ source.name }}
              </AppLink>
            </td>
            <td>{{ source.data_description }}</td>
            <td>{{ source.date }}</td>
            <td>{{ source.date_description }}</td>
            <td>
              <AppCopy
                v-tooltip="'Copy citation text to clipboard'"
                :text="getSourceCitation(source)"
              >
                <font-awesome-icon :icon="faFeatherPointed" />
              </AppCopy>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <AppHeading level="2">Suppressed Values</AppHeading>

    <p>
      In some cases, values may have been "suppressed", i.e. rounded down to 0
      or treated as "No Data". This is done to protect the privacy of
      individuals whose identities could be determined from the combination of a
      small value and a small population/geographic area. Depending on the data
      being viewed, the suppression was either already done in the original data
      source, or done in our pre-processing of the data. Thus, for a given
      feature on the map, it may be impossible to discriminate between a missing
      value, a true value of 0, and a very low value that was suppressed.
    </p>
  </section>

  <section v-for="(source, index) in sources" :key="index">
    <AppHeading :id="source.id" level="2">
      {{ source.name }} ({{ source.id }})
    </AppHeading>

    <div style="display: contents" v-html="descriptions[source.id]" />
  </section>

  <section>
    <AppHeading level="2">Cancer Disparities Index</AppHeading>

    <p>
      Burden data were used to rank every county using the cancer disparities
      index. Rankings are based on incidence, late-stage incidence, and
      mortality data provided by the Colorado Central Cancer Registry and Vital
      Statistics from CDPHE. Data are unavailable for some counties due to
      confidentiality or statistics reliability concerns.
    </p>

    <p>
      To develop the index, a Principal Components Analysis (PCA) was applied to
      the most recent burden data. PCA is a process used to detect the strongest
      patterns in a data set and to emphasize variation. Unlike other
      statistical methods, PCA makes very few assumptions about data. It is
      commonly used for data exploration and health index creation. PCA
      determines which variables summarize the overall data best and packages
      these variables that are most alike into new variables or “components”.
      Each of these new variables are given a weight based on how much of the
      overall data variation they explain and an index score is calculated. A
      higher disease disparity index (i.e., higher rank) will have a higher
      corresponding index score applied to the application.
    </p>
  </section>

  <section>
    <AppHeading level="2">Social Determinants of Health</AppHeading>

    <p>
      Social determinants of health (SDOH) are the conditions in the
      environments where people are born, live, learn, work, play, worship, and
      age that affect a wide range of health, functioning, and quality of life
      outcomes and risks. SDOH can be grouped into 5 domains: economic
      stability; education access and quality; health care access and quality;
      neighborhood and built environment; and social and community context. It
      has been shown that social determinants of health can affect lifestyle and
      therefore chronic diseases, including cancer.
    </p>

    <p>
      <AppLink
        to="https://health.gov/healthypeople/priority-areas/social-determinants-health"
      >
        See Healthy People 2030 for more information.
      </AppLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { kebabCase } from "lodash";
import { micromark } from "micromark";
import { gfmTable, gfmTableHtml } from "micromark-extension-gfm-table";
import { faFeatherPointed, faTable } from "@fortawesome/free-solid-svg-icons";
import { getDownloadAll, getSourceCitation, getSources } from "@/api";
import AppButton from "@/components/AppButton.vue";
import AppCopy from "@/components/AppCopy.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppLink from "@/components/AppLink.vue";
import AppStatus from "@/components/AppStatus.vue";
import { useQuery } from "@/util/composables";

/** load sources metadata */
const {
  query: loadSources,
  data: sources,
  status: sourcesStatus,
} = useQuery(getSources, undefined);

onMounted(loadSources);

/** load source description markdown files */
const descriptions = Object.fromEntries(
  Object.entries(import.meta.glob("./*.md", { as: "raw", eager: true })).map(
    ([key, value]) => [
      key.replace(/^\.\/(.*)\.md$/, "$1"),
      micromark(value, {
        extensions: [gfmTable()],
        htmlExtensions: [gfmTableHtml()],
      }),
    ],
  ),
);
</script>
