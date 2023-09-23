<template>
  <section class="full">
    <h2>Explore cancer data in {{ area }}</h2>

    <div v-if="status === 'success'" class="layout">
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
          :icon="faTable"
          :accent="true"
          >Download Data</AppButton
        >
        <AppButton
          v-tooltip="'Download current map view as PNG'"
          :icon="faMap"
          :accent="true"
          @click="downloadMap"
          >Download Map</AppButton
        >

        <hr />

        <div class="double-control">
          <AppCheckbox
            v-model="showLegend"
            v-tooltip="'Show/hide legend on map'"
            label="Show legend"
          />
          <AppCheckbox
            v-model="showDetails"
            v-tooltip="'Show/hide extra details in map legend'"
            label="Show details"
          />
        </div>

        <div class="double-control">
          <AppSlider
            v-model="dataOpacity"
            v-tooltip="'Transparency of map data layer'"
            label="Data opacity"
          />
          <AppSlider
            v-model="baseOpacity"
            v-tooltip="'Transparency of map base layer'"
            label="Base opacity"
          />
        </div>

        <AppAccordion label="More Options">
          <AppSelect
            v-model="selectedBase"
            v-tooltip="'Provider to use for base map layer'"
            label="Base layer"
            :options="baseOptions"
          />

          <AppSelect
            v-model="selectedGradient"
            v-tooltip="'Gradient to use for coloring map data'"
            label="Gradient"
            :options="gradientOptions"
          />

          <div class="double-control">
            <AppCheckbox
              v-model="flipGradient"
              v-tooltip="'Reverse direction of color gradient'"
              label="Flip gradient"
            />
          </div>

          <div class="double-control">
            <AppNumber
              v-model="scaleSteps"
              v-tooltip="
                'Number of steps to divide data scale into. Only approximate if &quot;nice steps&quot; on.'
              "
              :min="3"
              :max="20"
              :step="1"
              label="Scale steps"
            />
            <AppCheckbox
              v-model="niceSteps"
              v-tooltip="'Round scale steps to nice, even intervals'"
              label="Nice steps"
            />
          </div>

          <label
            v-tooltip="
              'Dimensions of map, useful to set exactly when downloading as image. Use 0 to fit to window.'
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

      <div class="map-container">
        <div
          ref="mapContainer"
          class="map"
          :style="{ opacity: geometryStatus === 'loading' ? 0.5 : 1 }"
        >
          <AppMap
            ref="map"
            v-model:zoom="zoom"
            v-model:lat="lat"
            v-model:long="long"
            :geometry="selectedGeometry"
            :values="values?.values"
            :min="values?.min"
            :max="values?.max"
            :show-legend="showLegend"
            :show-details="showDetails"
            :data-opacity="dataOpacity"
            :base-opacity="baseOpacity"
            :base="selectedBase"
            :gradient="selectedGradient"
            :flip-gradient="flipGradient"
            :scale-steps="scaleSteps"
            :nice-steps="niceSteps"
            :width="mapWidth"
            :height="mapHeight"
            :scroll-zoom="!mapScrollable"
          >
            <template #heading>
              <strong>{{ measures[selectedMeasure]?.label }}</strong>
              <small>({{ categories[selectedCategory]?.label }})</small>
              <small>by {{ levels[selectedLevel]?.label }}</small>
            </template>

            <template #details>
              <div class="mini-table">
                <span>Min:</span>
                <span>
                  {{ formatValue(values?.min, values?.min, values?.max) }}</span
                >
                <span>Max:</span>
                <span>
                  {{ formatValue(values?.max, values?.min, values?.max) }}</span
                >
                <span>Mean:</span>
                <span>
                  {{
                    formatValue(values?.mean, values?.min, values?.max)
                  }}</span
                >
                <span>Median:</span>
                <span>
                  {{
                    formatValue(values?.median, values?.min, values?.max)
                  }}</span
                >
              </div>
            </template>
          </AppMap>
        </div>

        <div class="controls">
          <AppButton
            aria-label="Zoom out of map"
            :icon="faMinus"
            @click="map?.zoomOut()"
          />
          <AppButton
            aria-label="Zoom in of map"
            :icon="faPlus"
            @click="map?.zoomIn()"
          />
          <AppButton
            aria-label="Fit map view"
            :icon="faCropSimple"
            @click="map?.fit"
          >
            Fit
          </AppButton>
        </div>
      </div>
    </div>

    <AppStatus v-else :status="status" />
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
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { cloneDeep } from "lodash";
import { faMap } from "@fortawesome/free-regular-svg-icons";
import {
  faCropSimple,
  faMinus,
  faPlus,
  faTable,
} from "@fortawesome/free-solid-svg-icons";
import {
  getFacets,
  getGeometry,
  getValues,
  type Facet,
  type Facets,
  type Geometry,
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
  booleanParam,
  numberParam,
  stringParam,
  useScrollable,
  useUrlParam,
} from "@/util/composables";
import { formatValue } from "@/util/math";
import "leaflet/dist/leaflet.css";

// project info
const { VITE_AREA: area } = import.meta.env;

// element refs
const panel = ref<HTMLElement>();
const mapContainer = ref<HTMLElement>();
const map = ref<InstanceType<typeof AppMap>>();

// show gradients on elements when scrollable
useScrollable(panel);
const mapScrollable = useScrollable(mapContainer);

// data state
const status = ref<Status>("loading");
const geometryStatus = ref<Status>("loading");
const counties = ref<Geometry>();
const tracts = ref<Geometry>();
const selectedGeometry = ref<Geometry>();
const facets = ref<Facets>();
const values = ref<Values>();

// select boxes state
const selectedLevel = useUrlParam("level", stringParam, "");
const selectedCategory = useUrlParam("category", stringParam, "");
const selectedMeasure = useUrlParam("measure", stringParam, "");

// map zoom state
const zoom = useUrlParam("zoom", numberParam, 0);
const lat = useUrlParam("lat", numberParam, 0);
const long = useUrlParam("long", numberParam, 0);

// map style state
const showLegend = ref(true);
const showDetails = ref(false);
const dataOpacity = ref(0.75);
const selectedBase = useUrlParam("base", stringParam, baseOptions[0]?.id || "");
const baseOpacity = ref(1);
const selectedGradient = useUrlParam(
  "grad",
  stringParam,
  gradientOptions[0]?.id || "",
);
const flipGradient = useUrlParam("flip", booleanParam, false);
const scaleSteps = ref(5);
const niceSteps = ref(true);
const mapWidth = ref(0);
const mapHeight = ref(0);

// load hierarchy of geographic levels, measure categories, and measures
async function loadFacets() {
  try {
    facets.value = await getFacets();
    status.value = "success";
  } catch (error) {
    console.error(error);
    status.value = "error";
  }
}
loadFacets();

// load and select geometry data to display on map, on request to save bandwidth
watchEffect(async () => {
  try {
    geometryStatus.value = "loading";
    // clear geometry while loading
    selectedGeometry.value = undefined;
    if (selectedLevel.value === "county")
      selectedGeometry.value =
        counties.value || (await getGeometry("counties", "us_fips"));
    else if (selectedLevel.value === "tract")
      selectedGeometry.value =
        tracts.value || (await getGeometry("tracts", "fips"));
    geometryStatus.value = "success";
  } catch (error) {
    console.error(error);
    geometryStatus.value = "error";
  }
});

// load map values data
watchEffect(async () => {
  if (!(selectedLevel.value && selectedCategory.value && selectedMeasure.value))
    return;
  values.value = await getValues(
    selectedLevel.value,
    selectedCategory.value,
    selectedMeasure.value,
  );
});

// geographic levels from facets data
const levels = computed(() => cloneDeep(facets.value || {}));

// measure categories from geographic level
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.list || {}),
);

// measures from measure category
const measures = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.list || {}),
);

// turn facet into list of select box options
function facetToOptions(facet: Facet): Option[] {
  return Object.values(facet).map(({ id, label }) => ({ id, label }));
}

// auto-select level option
watch([levels], () => {
  // if not already selected, or selection no longer valid
  if (!selectedLevel.value || !levels.value[selectedLevel.value])
    selectedLevel.value = Object.keys(levels.value)[0] || "";
});

// auto-select category
watch([selectedLevel, categories], () => {
  if (!selectedCategory.value || !categories.value[selectedCategory.value])
    selectedCategory.value = Object.keys(categories.value)[0] || "";
});

// auto-select measure
watch([selectedCategory, measures], () => {
  if (!selectedMeasure.value || !measures.value[selectedMeasure.value])
    selectedMeasure.value = Object.keys(measures.value)[0] || "";
});

// download map with filename
function downloadMap() {
  map.value?.download([selectedMeasure.value, selectedLevel.value]);
}
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  margin: 40px 0;
  gap: 30px;
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

.double-control {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: flex-end;
  width: 100%;
  gap: 10px 20px;
}

@media (max-width: 400px) {
  .double-control {
    grid-template-columns: 1fr;
  }
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

.controls {
  display: flex;
  gap: 10px;
}

.map-container {
  display: flex;
  position: sticky;
  top: 20px;
  flex-direction: column;
  width: 0;
  min-width: 100%;
  max-height: calc(100vh - 35px);
  gap: 20px;
}

.map {
  flex-grow: 1;
  overflow: auto;
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
</style>
