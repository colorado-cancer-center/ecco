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
          label="Variable category"
          :options="facetToOptions(categories)"
        />
        <AppSelect
          v-model="selectedVariable"
          label="Variable"
          :options="facetToOptions(variables)"
        />

        <AppButton :icon="faTable" :accent="true">Download Data</AppButton>
        <AppButton :icon="faMap" :accent="true" @click="downloadMap"
          >Download Map</AppButton
        >

        <AppAccordion label="Map Styling">
          <AppCheckbox v-model="showLegend" label="Show legend" />
          <AppSelect
            v-model="selectedGradient"
            label="Gradient"
            :options="gradientOptions"
          />
          <AppCheckbox v-model="flipGradient" label="Flip gradient" />
          <AppNumber
            v-model="mapWidth"
            label="Map width"
            :max="2000"
            :step="10"
          />
          <AppNumber
            v-model="mapHeight"
            label="Map height"
            :max="2000"
            :step="10"
          />
          <AppSlider v-model="baseOpacity" label="Base layer opacity" />
          <AppSlider v-model="dataOpacity" label="Data layer opacity" />
        </AppAccordion>
      </div>

      <div ref="mapContainer" class="map-container">
        <AppMap
          ref="map"
          v-model:zoom="zoom"
          v-model:lat="lat"
          v-model:long="long"
          :geometry="geometry"
          :base-opacity="baseOpacity"
          :data-opacity="dataOpacity"
          :values="values?.values"
          :min="values?.min"
          :max="values?.max"
          :gradient="selectedGradient"
          :flip-gradient="flipGradient"
          :show-legend="showLegend"
          :width="mapWidth"
          :height="mapHeight"
        >
          <template #legend>
            <strong>{{ variables[selectedVariable]?.name }}</strong>
            <small>({{ categories[selectedCategory]?.name }})</small>
            <small>by {{ levels[selectedLevel]?.name }}</small>
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
  getGeometry,
  getMeasures,
  getValues,
  type Facet,
  type Geometry,
  type Measures,
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
import {
  booleanParam,
  numberParam,
  stringParam,
  useScrollable,
  useUrlParam,
} from "@/util/composables";
import "leaflet/dist/leaflet.css";

// project info
const { VITE_AREA: area } = import.meta.env;

// element refs
const panel = ref<HTMLElement>();
const mapContainer = ref<HTMLElement>();
const map = ref<InstanceType<typeof AppMap>>();

// show gradients on elements when scrollable
useScrollable(panel);
useScrollable(mapContainer);

// data state
const status = ref<Status>("loading");
const counties = ref<Geometry>();
const tracts = ref<Geometry>();
const measures = ref<Measures>();
const values = ref<Values>();

// select boxes state
const selectedLevel = useUrlParam("level", stringParam, "");
const selectedCategory = useUrlParam("category", stringParam, "");
const selectedVariable = useUrlParam("variable", stringParam, "");

// map zoom state
const zoom = useUrlParam("zoom", numberParam, 0);
const lat = useUrlParam("lat", numberParam, 0);
const long = useUrlParam("long", numberParam, 0);

// map style state
const showLegend = ref(true);
const selectedGradient = useUrlParam(
  "grad",
  stringParam,
  gradientOptions[0]?.id || "",
);
const flipGradient = useUrlParam("flip-grad", booleanParam, false);
const baseOpacity = ref(1);
const dataOpacity = ref(0.75);
const mapWidth = ref(0);
const mapHeight = ref(0);

// load map and measure data
async function loadData() {
  try {
    const [countiesData, tractsData, measureData] = await Promise.all([
      getGeometry("counties", "us_fips"),
      getGeometry("tracts", "fips"),
      getMeasures(),
    ]);
    status.value = "success";
    counties.value = countiesData;
    tracts.value = tractsData;
    measures.value = measureData;
  } catch (error) {
    console.error(error);
    status.value = "error";
  }
}
loadData();

// load map values data
watchEffect(async () => {
  if (
    !(selectedLevel.value && selectedCategory.value && selectedVariable.value)
  )
    return;
  values.value = await getValues(
    selectedLevel.value,
    selectedCategory.value,
    selectedVariable.value,
  );
});

// geographic levels from data
const levels = computed(() => cloneDeep(measures.value || {}));

// variable categories from geographic level
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.children || {}),
);

// variables from variable category
const variables = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.children || {}),
);

// turn facet into list of select box options
function facetToOptions(facet: Facet): Option[] {
  return Object.values(facet).map(({ id, name }) => ({ id, name }));
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

// auto-select variable
watch([selectedCategory, variables], () => {
  if (!selectedVariable.value || !variables.value[selectedVariable.value])
    selectedVariable.value = Object.keys(variables.value)[0] || "";
});

// geometry data to display on map
const geometry = computed(() => {
  let geometry = counties.value;
  if (selectedLevel.value === "tract") geometry = tracts.value;
  return geometry;
});

// download map with filename
function downloadMap() {
  map.value?.download([selectedVariable.value, selectedLevel.value]);
}
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-rows: 1fr min-content;
  grid-template-columns: 300px 1fr;
  grid-template-areas:
    "panel map"
    "panel controls";
  grid-auto-flow: row;
  min-height: 75vh;
  margin: 40px 0;
  gap: 30px;
}

.panel {
  display: flex;
  grid-area: panel;
  flex-direction: column;
  align-items: stretch;
  height: 0; /* remove from height calculation */
  min-height: 100%; /* match other row's height */
  margin: 0;
  padding: 0;
  padding-right: 10px;
  overflow-y: auto;
  gap: 20px;
  border: none;
  border-radius: var(--rounded);
}

.controls {
  display: flex;
  grid-area: controls;
  gap: 10px;
}

.map-container {
  grid-area: map;
  overflow: auto;
}

@media (max-width: 800px) {
  .layout {
    grid-template-rows: max-content minmax(400px, 1fr) min-content;
    grid-template-columns: 1fr;
    grid-template-areas:
      "panel"
      "map"
      "controls";
  }

  .panel {
    height: unset;
    min-height: unset;
    overflow-y: unset;
  }

  .layout > * {
    min-width: 0;
  }
}
</style>
