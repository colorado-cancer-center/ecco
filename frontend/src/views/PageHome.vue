<template>
  <section class="full">
    <h2>Explore cancer data in {{ area }}</h2>

    <div v-if="defsStatus === 'success'" class="layout">
      <!-- https://bugs.chromium.org/p/chromium/issues/detail?id=1484663 -->
      <div ref="panel" class="panel" role="group">
        <AppSelect
          v-model="selectedLevel"
          label="Geographic level"
          :options="facetToOptions(levels)"
        />

        <AppSelect
          v-model="selectedCategory"
          label="Measure category"
          :options="facetToOptions(categories)"
        />

        <AppSelect
          v-model="selectedMeasure"
          label="Measure"
          :options="facetToOptions(measures)"
        />

        <AppButton
          v-tooltip="'Download selected data in CSV format'"
          :icon="faDownload"
          :to="
            getDataDownload(selectedLevel, selectedCategory, selectedMeasure)
          "
          :accent="true"
          >Download Data</AppButton
        >

        <hr />

        <AppSelect
          v-model="selectedOverlays"
          label="Overlays"
          :options="overlayOptions"
          :multi="true"
          tooltip="Locations to show on map"
        />

        <div class="multi-control">
          <AppCheckbox
            v-model="showLegends"
            v-tooltip="'Show/hide legend panels on map'"
            label="Show legends"
          />

          <AppCheckbox
            v-model="showStats"
            v-tooltip="'Show/hide extra stats in legends'"
            label="Show stats"
          />
        </div>

        <AppAccordion label="More Options">
          <AppSelect
            v-model="selectedGradient"
            v-tooltip="'Gradient to use for coloring map data'"
            label="Gradient"
            :options="gradientOptions"
          >
            <template #preview="{ option }">
              <svg
                :viewBox="`0 0 10 1`"
                preserveAspectRatio="none"
                class="gradient-preview"
              >
                <defs>
                  <linearGradient :id="option?.id">
                    <stop
                      v-for="(color, index) in option?.colors"
                      :key="index"
                      :offset="
                        100 * (index / ((option?.colors.length || 1) - 1)) + '%'
                      "
                      :stop-color="color"
                    />
                  </linearGradient>
                </defs>
                <rect
                  :fill="`url('#${option?.id}')`"
                  x="0"
                  y="0"
                  width="10"
                  height="1"
                />
              </svg>
            </template>
          </AppSelect>

          <AppCheckbox
            v-model="flipGradient"
            v-tooltip="'Reverse direction of color gradient'"
            label="Flip gradient"
          />

          <AppSelect
            v-model="selectedBase"
            label="Base layer"
            :options="baseOptions"
            tooltip="Provider to use for base map layer"
          >
            <template #preview="{ option }">
              <div class="image-preview">
                <img :src="option?.image" alt="" />
              </div>
            </template>
          </AppSelect>

          <div class="multi-control">
            <AppNumber
              v-model="scalePower"
              v-tooltip="
                `
                Power to raise step ranges by. Only affects which colors are assigned to which values.
                <br />
                <br />
                = 1 is linear
                <br />
                > 1 exaggerates differences at low values
                <br />
                < 1 exaggerates differences at high values
                `
              "
              :min="scalePower < 1 ? 0.05 : 0"
              :max="10"
              :step="scalePower < 1 ? 0.05 : 0.5"
              label="Scale power"
            />

            <AppNumber
              v-model="scaleSteps"
              v-tooltip="
                'Number of bins to divide data into for coloring. Only approximate if &quot;nice steps&quot; on.'
              "
              :min="2"
              :max="10"
              :step="1"
              label="Scale steps"
            />
          </div>

          <div class="multi-control">
            <AppCheckbox
              v-model="niceSteps"
              v-tooltip="
                'Adjust number of scale steps to get nice, round intervals (when power 1)'
              "
              label="Nice steps"
            />
          </div>

          <div class="multi-control">
            <AppSlider
              v-model="baseOpacity"
              v-tooltip="'Transparency of map base layer'"
              label="Base trans."
            />

            <AppSlider
              v-model="dataOpacity"
              v-tooltip="'Transparency of map data layer'"
              label="Data trans."
            />

            <AppSlider
              v-model="overlayOpacity"
              v-tooltip="'Transparency of map overlays'"
              label="Over. trans."
            />
          </div>

          <label
            v-tooltip="
              'Exact dimensions of map. Useful to set before downloading as image. Leave as 0 to fit to page.'
            "
            class="dimensions-label"
          >
            <span>Map dimensions</span>
            <div class="dimensions">
              <AppNumber
                v-model="mapWidth"
                label="Map width"
                :hide-label="true"
                :max="2000"
                :step="100"
              />
              <span> &times; </span>
              <AppNumber
                v-model="mapHeight"
                label="Map height"
                :hide-label="true"
                :max="2000"
                :step="100"
              />
            </div>
          </label>
        </AppAccordion>
      </div>

      <AppMap
        v-model:zoom="zoom"
        v-model:lat="lat"
        v-model:long="long"
        class="map"
        :style="{ opacity: dataStatus === 'loading' ? 0.25 : 1 }"
        :data="selectedData"
        :overlays="_overlays"
        :values="values?.values"
        :min="values?.min"
        :max="values?.max"
        :show-legends="showLegends"
        :base-opacity="baseOpacity"
        :data-opacity="dataOpacity"
        :overlay-opacity="overlayOpacity"
        :base="selectedBase"
        :gradient="selectedGradient"
        :flip-gradient="flipGradient"
        :scale-steps="scaleSteps"
        :nice-steps="niceSteps"
        :scale-power="scalePower"
        :width="mapWidth"
        :height="mapHeight"
        :filename="[selectedMeasure, selectedLevel]"
      >
        <template #top-left>
          <div>
            <strong>{{ measures[selectedMeasure]?.label }}</strong>
            <br />
            <small> {{ categories[selectedCategory]?.label }} </small>
            <br />
            <small>by {{ levels[selectedLevel]?.label }}</small>
          </div>

          <template v-if="showStats">
            <div class="mini-table">
              <span>Min</span>
              <span
                v-tooltip="
                  formatValue(values?.min, values?.min, values?.max, false)
                "
              >
                {{ formatValue(values?.min, values?.min, values?.max) }}
              </span>
              <span>Max</span>
              <span
                v-tooltip="
                  formatValue(values?.max, values?.min, values?.max, false)
                "
              >
                {{ formatValue(values?.max, values?.min, values?.max) }}
              </span>
              <span>Mean</span>
              <span
                v-tooltip="
                  formatValue(values?.mean, values?.min, values?.max, false)
                "
              >
                {{ formatValue(values?.mean, values?.min, values?.max) }}
              </span>
              <span>Median</span>
              <span
                v-tooltip="
                  formatValue(values?.median, values?.min, values?.max, false)
                "
              >
                {{ formatValue(values?.median, values?.min, values?.max) }}
              </span>
            </div>
          </template>
        </template>
      </AppMap>
    </div>

    <AppStatus v-else :status="defsStatus" />
  </section>

  <section>
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
      veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
      commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
      velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
      cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
      est laborum.
    </p>

    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
      veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
      commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
      velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
      cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
      est laborum.
    </p>
    <AppButton to="/about">Learn More</AppButton>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { cloneDeep, pick } from "lodash";
import { faDownload } from "@fortawesome/free-solid-svg-icons";
import {
  getData,
  getDataDownload,
  getFacets,
  getOverlays,
  getValues,
  type Data,
  type Facet,
  type Facets,
  type Overlays,
  type Values,
} from "@/api";
import AppAccordion from "@/components/AppAccordion.vue";
import AppButton from "@/components/AppButton.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppMap from "@/components/AppMap.vue";
import AppNumber from "@/components/AppNumber.vue";
import AppSelect, { type Option } from "@/components/AppSelect.vue";
import AppSlider from "@/components/AppSlider.vue";
import AppStatus, { type Status } from "@/components/AppStatus.vue";
import { gradientOptions } from "@/components/gradient";
import { baseOptions } from "@/components/tile-providers";
import {
  arrayParam,
  numberParam,
  stringParam,
  useScrollable,
  useUrlParam,
} from "@/util/composables";
import { formatValue } from "@/util/math";

/** project info */
const { VITE_AREA: area } = import.meta.env;

/** element refs */
const panel = ref<HTMLElement>();

/** show gradients on elements when scrollable */
useScrollable(panel);

/** data state */
const defsStatus = ref<Status>("loading");
const dataStatus = ref<Status>("loading");
const counties = ref<Data>();
const tracts = ref<Data>();
const selectedData = ref<Data>();
const facets = ref<Facets>();
const values = ref<Values>();
const overlays = ref<Overlays>();

/** select boxes state */
const selectedLevel = useUrlParam("level", stringParam, "");
const selectedCategory = useUrlParam("category", stringParam, "");
const selectedMeasure = useUrlParam("measure", stringParam, "");

/** map zoom state */
const zoom = useUrlParam("zoom", numberParam, 0);
const lat = useUrlParam("lat", numberParam, 0);
const long = useUrlParam("long", numberParam, 0);

/** map style state */
const showLegends = ref(true);
const showStats = ref(false);
const selectedBase = ref(baseOptions[0]?.id || "");
const selectedGradient = ref(gradientOptions[3]?.id || "");
const selectedOverlays = useUrlParam("overlays", arrayParam(stringParam), []);
const baseOpacity = ref(1);
const dataOpacity = ref(0.75);
const overlayOpacity = ref(1);
const flipGradient = ref(false);
const scaleSteps = ref(6);
const niceSteps = ref(true);
const scalePower = ref(1);
const mapWidth = ref(0);
const mapHeight = ref(0);

/** get "core" data once on page load */
async function loadDefs() {
  try {
    defsStatus.value = "loading";
    facets.value = await getFacets();
    overlays.value = await getOverlays();
    defsStatus.value = "success";
  } catch (error) {
    console.error(error);
    defsStatus.value = "error";
  }
}
loadDefs();

/** load and select geometry data to display on map, on request to save bandwidth */
watchEffect(async () => {
  try {
    dataStatus.value = "loading";
    /** clear geometry while loading */
    selectedData.value = undefined;

    /** choose and fetch data */
    if (selectedLevel.value === "county") {
      counties.value ??= await getData("counties", "us_fips");
      selectedData.value = counties.value;
    } else if (selectedLevel.value === "tract") {
      tracts.value ??= await getData("tracts", "fips");
      selectedData.value = tracts.value;
    }

    dataStatus.value = "success";
  } catch (error) {
    console.error(error);
    dataStatus.value = "error";
  }
});

/** load map values data */
watchEffect(async () => {
  if (selectedLevel.value && selectedCategory.value && selectedMeasure.value)
    values.value = await getValues(
      selectedLevel.value,
      selectedCategory.value,
      selectedMeasure.value,
    );
});

/** geographic levels from facets data */
const levels = computed(() => cloneDeep(facets.value || {}));

/** measure categories from geographic level */
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.list || {}),
);

/** measures from measure category */
const measures = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.list || {}),
);

/** turn facet into list of select box options */
function facetToOptions(facet: Facet): Option[] {
  return Object.values(facet).map(({ id, label }) => ({ id, label }));
}

/** auto-select level option */
watch([levels], () => {
  /** if not already selected, or selection no longer valid */
  if (!selectedLevel.value || !levels.value[selectedLevel.value])
    selectedLevel.value = Object.keys(levels.value)[0] || "";
});

/** auto-select category */
watch([selectedLevel, categories], () => {
  if (!selectedCategory.value || !categories.value[selectedCategory.value])
    selectedCategory.value = categories.value["sociodemographics"]
      ? "sociodemographics"
      : Object.keys(categories.value)[0] || "";
});

/** auto-select measure */
watch([selectedCategory, measures], () => {
  if (!selectedMeasure.value || !measures.value[selectedMeasure.value])
    selectedMeasure.value = measures.value["Total"]
      ? "Total"
      : Object.keys(measures.value)[0] || "";
});

/** overlay dropdown options */
const overlayOptions = computed<Option[]>(() =>
  Object.entries(overlays.value || {}).map(([key, value]) => ({
    id: key,
    label: value.label,
  })),
);

/** overlay data to pass to map, filtered by selected overlays */
const _overlays = computed(
  () => pick(overlays.value, selectedOverlays.value) as Overlays | undefined,
);
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  margin: 40px 0;
  gap: 20px;
}

.panel {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  margin: 0;
  padding: 0;
  padding-right: 10px;
  gap: 20px;
  border: none;
  border-radius: var(--rounded);
}

.multi-control {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  align-items: flex-end;
  width: 100%;
  gap: 10px;
}

.dimensions-label {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
  cursor: pointer;
}

.dimensions {
  display: grid;
  grid-template-columns: 1fr min-content 1fr;
  align-items: center;
  gap: 5px;
}

.map {
  position: sticky;
  top: 20px;
  width: 0;
  min-width: 100%;
  height: calc(100vh - 40px);
  transition: opacity var(--fast);
}

@media (max-width: 800px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .map {
    height: 90vh;
  }
}

.gradient-preview {
  max-width: 100px;
  height: 1em;
}

.image-preview {
  flex-shrink: 0;
  width: 2em;
  height: 2em;
  overflow: hidden;
  background: var(--light-gray);
}

.image-preview img {
  width: 100%;
  height: 100%;
  /* center map on particular place (continental US) */
  transform: scale(4.9) translate(28%, 15.4%);
}
</style>
