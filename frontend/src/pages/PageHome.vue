<template>
  <AppAlert>
    <p>
      This site is still in <strong>beta</strong>. Please
      <AppLink to="/about#contact">let us know how we can improve it!</AppLink>
    </p>
    <p>
      We encourage using this for non-critical applications of research,
      outreach, and similar purposes. It should not be used to support clinical
      decisions.
    </p>
  </AppAlert>

  <section class="full">
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

        <AppButton
          v-tooltip="'Download selected category data in CSV format'"
          :icon="faDownload"
          :to="getDownload(selectedLevel, selectedCategory)"
          :accent="true"
        >
          Download Category
        </AppButton>

        <AppSelect
          v-model="selectedMeasure"
          label="Measure"
          :options="facetToOptions(measures)"
        />

        <AppButton
          v-tooltip="'Download selected measure data in CSV format'"
          :icon="faDownload"
          :to="getDownload(selectedLevel, selectedCategory, selectedMeasure)"
          :accent="true"
        >
          Download Measure
        </AppButton>

        <template v-for="(factor, key) in factors" :key="key">
          <AppSelect
            v-if="selectedFactors[key]"
            :model-value="selectedFactors[key]!.value"
            :label="factor.label"
            :options="
              Object.entries(factor.values).map(([key, value]) => ({
                id: key,
                label: value,
              }))
            "
            @update:model-value="
              (value) => (selectedFactors[key]!.value = [value].flat()[0] || '')
            "
          />
        </template>

        <AppLink :to="learnMoreLink" :new-tab="true">
          <font-awesome-icon :icon="faQuestionCircle" class="icon" />
          Learn more about selected data
        </AppLink>

        <hr />

        <AppSelect
          v-model="selectedLocations"
          label="Locations"
          :options="locationOptions"
          :multi="true"
          tooltip="Locations to show on map, e.g. screening centers, clinics,
      specialists"
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
                'Number of bins to divide data into for coloring. If &quot;nice steps&quot; on, only approximate.'
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
              v-model="locationOpacity"
              v-tooltip="'Transparency of map locations'"
              label="Loc. trans."
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

        <AppButton
          v-tooltip="'Reset selected options and map to default'"
          :icon="faArrowsRotate"
          :flip="true"
          :accent="true"
          @click="reset"
          >Reset</AppButton
        >
      </div>

      <AppMap
        v-if="renderMap"
        ref="map"
        v-model:zoom="zoom"
        v-model:lat="lat"
        v-model:long="long"
        class="map"
        :style="{
          opacity: dataStatus === 'loading' ? 0.25 : 1,
          height: autoMapHeight,
        }"
        :data="selectedData"
        :locations="_locations"
        :values="values?.values"
        :min="values?.min"
        :max="values?.max"
        :show-legends="showLegends"
        :base-opacity="baseOpacity"
        :data-opacity="dataOpacity"
        :location-opacity="locationOpacity"
        :base="selectedBase"
        :gradient="selectedGradient"
        :flip-gradient="flipGradient"
        :scale-steps="scaleSteps"
        :nice-steps="niceSteps"
        :scale-power="scalePower"
        :explicit-scale="
          selectedCategory.includes('trend')
            ? { 1: 'Falling', 2: 'Stable', 3: 'Rising' }
            : undefined
        "
        :width="mapWidth"
        :height="mapHeight"
        :filename="[selectedMeasure, selectedLevel]"
        @no-data="(value) => (noData = value)"
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
              <template v-if="typeof values?.min === 'number'">
                <span>Min</span>
                <span v-tooltip="formatValue(values?.min, percent, false)">
                  {{ formatValue(values?.min, percent) }}
                </span>
              </template>

              <template v-if="typeof values?.max === 'number'">
                <span>Max</span>
                <span v-tooltip="formatValue(values?.max, percent, false)">
                  {{ formatValue(values?.max, percent) }}
                </span>
              </template>

              <template v-if="typeof values?.mean === 'number'">
                <span>Mean</span>
                <span v-tooltip="formatValue(values?.mean, percent, false)">
                  {{ formatValue(values?.mean, percent) }}
                </span>
              </template>

              <template v-if="typeof values?.median === 'number'">
                <span>Median</span>
                <span v-tooltip="formatValue(values?.median, percent, false)">
                  {{ formatValue(values?.median, percent) }}
                </span>
              </template>
            </div>
          </template>
        </template>

        <template v-if="noData" #top-right>
          <small>
            "No data" may indicate unavailable data, zero, or a low value
            suppressed for privacy reasons.
          </small>
        </template>
      </AppMap>
    </div>

    <AppStatus v-else :status="defsStatus" />
  </section>

  <section>
    <p>
      Welcome to
      <b>E</b>xploring <b>C</b>ancer in <b>Co</b>lorado (<b>ECCO</b>), an
      interactive resource for exploring cancer data in Colorado. You can view
      per-region data for things like population, demographics, cancer burden,
      risk factors, cancer disparities, health behaviors, environmental
      exposures, and more. You can also see local resources for cancer
      prevention, screening, treatment, survivorship, and more.
    </p>

    <div class="center">
      <AppButton to="/about" :icon="faArrowRight" :flip="true" :accent="true"
        >Learn more</AppButton
      >
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  computed,
  onUnmounted,
  ref,
  shallowRef,
  watch,
  watchEffect,
  type ShallowRef,
  type WatchStopHandle,
} from "vue";
import { cloneDeep, mapValues, pick } from "lodash";
import { faQuestionCircle } from "@fortawesome/free-regular-svg-icons";
import {
  faArrowRight,
  faArrowsRotate,
  faDownload,
} from "@fortawesome/free-solid-svg-icons";
import { useElementBounding } from "@vueuse/core";
import {
  getDownload,
  getFacets,
  getGeo,
  getLocations,
  getValues,
  type Data,
  type Facet,
  type Facets,
  type Locations,
  type Values,
} from "@/api";
import locationGroups from "@/api/location-groups.json";
import AppAccordion from "@/components/AppAccordion.vue";
import AppAlert from "@/components/AppAlert.vue";
import AppButton from "@/components/AppButton.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppLink from "@/components/AppLink.vue";
import AppMap from "@/components/AppMap.vue";
import AppNumber from "@/components/AppNumber.vue";
import AppSelect, { type Entry, type Option } from "@/components/AppSelect.vue";
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
import { formatValue, isPercent } from "@/util/math";
import { sleep } from "@/util/misc";

/** get "learn more" link based on selections */
const learnMoreLink = computed(() => {
  switch (selectedCategory.value) {
    case "cancerincidence":
    case "cancermortality":
      return "/sources#cancer-incidence-and-mortality";
    case "sociodemographics":
    case "economy":
    case "housingtrans":
      return "/sources#sociodemographics-economics-insurance-and-housing-transportation";
    case "rfandscreening":
      return "/sources#screening-risk-factors-and-other-health-factors";
    case "environment":
      return "/sources#environment";
    case "cancerdisparitiesindex":
      return "/sources#cancer-disparities-index";
  }

  return "/sources";
});

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
const locations = ref<Locations>();

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
const selectedLocations = useUrlParam("locations", arrayParam(stringParam), []);
const baseOpacity = ref(1);
const dataOpacity = ref(0.75);
const locationOpacity = ref(1);
const flipGradient = ref(false);
const scaleSteps = ref(6);
const niceSteps = ref(false);
const scalePower = ref(1);
const mapWidth = ref(0);
const mapHeight = ref(0);

/** whether map has any "no data" regions */
const noData = ref(false);

/** flag to force rerender of map */
const renderMap = ref(true);

/** reset controls and map to defaults */
async function reset() {
  /**
   * force full re-render of map. don't do this via key method to make sure
   * entire dom completely unmounted and recreated from scratch (no diffing by
   * vue)
   */
  renderMap.value = false;
  await sleep(100);
  renderMap.value = true;

  // selectedLevel.value = "";
  // selectedCategory.value = "";
  // selectedMeasure.value = "";
  zoom.value = 0;
  lat.value = 0;
  long.value = 0;
  showLegends.value = true;
  showStats.value = false;
  selectedBase.value = baseOptions[0]?.id || "";
  selectedGradient.value = gradientOptions[3]?.id || "";
  selectedLocations.value = [];
  baseOpacity.value = 1;
  dataOpacity.value = 0.75;
  locationOpacity.value = 1;
  flipGradient.value = false;
  scaleSteps.value = 6;
  niceSteps.value = false;
  scalePower.value = 1;
  mapWidth.value = 0;
  mapHeight.value = 0;
}

/** get "core" data once on page load */
async function loadDefs() {
  try {
    defsStatus.value = "loading";
    facets.value = await getFacets();
    locations.value = await getLocations();
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
      counties.value ??= await getGeo("counties", "us_fips");
      selectedData.value = counties.value;
    } else if (selectedLevel.value === "tract") {
      tracts.value ??= await getGeo("tracts", "fips");
      selectedData.value = tracts.value;
    }

    dataStatus.value = "success";
  } catch (error) {
    console.error(error);
    dataStatus.value = "error";
  }
});

/** geographic levels from facets data */
const levels = computed(() => cloneDeep(facets.value || {}));

/** measure categories from geographic level */
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.list || {}),
);

/** keep track of latest query */
let latest: Symbol;

/** load map values data */
async function loadValues() {
  if (!selectedLevel.value || !selectedCategory.value || !selectedMeasure.value)
    return;

  /** assign unique id to query */
  latest = Symbol();
  const current = latest;

  const result = await getValues(
    selectedLevel.value,
    selectedCategory.value,
    selectedMeasure.value,
    /** unwrap nested refs */
    mapValues(selectedFactors.value, (value) => value.value),
  );

  /** check if current query is latest (prevents race conditions) */
  if (current === latest) values.value = result;
  else console.debug("stale");
}

/** measures from measure category */
const measures = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.list || {}),
);

/** stratification factors (e.g. race/ethnicity, sex, etc) */
const factors = computed(() =>
  cloneDeep(measures.value[selectedMeasure.value]?.factors || {}),
);

/** selected value state for each factor */
const selectedFactors = shallowRef<{ [key: string]: ShallowRef<string> }>({});

/** keep track of dynamically created factor watchers */
let stoppers: WatchStopHandle[] = [];

/** clear all factor watchers */
const clearFactorWatchers = () => {
  stoppers.forEach((stopper) => stopper());
  stoppers = [];
};

/** cleanup factor watchers */
onUnmounted(clearFactorWatchers);

/** update selected factors when full set of factor options changes */
watch(
  factors,
  () => {
    /** all previous watchers irrelevant now */
    clearFactorWatchers();

    /** add selected that are new to options */
    for (const [key, value] of Object.entries(factors.value)) {
      /** ref 2-way synced with url */
      const factor = useUrlParam(
        key,
        stringParam,
        /** default selected */
        value.values["All"] ? "All" : Object.keys(value.values)[0] || "",
      );
      /** hook up url reactive with selected factor */
      selectedFactors.value[key] = factor;

      /** dynamically create watchers for factor */

      stoppers.push(
        /** when factor value changes */
        watch(
          factor,
          () => {
            /** get non-stale factor options */
            const options = factors.value[key]?.values || {};
            /** if value isn't valid anymore */
            if (!(factor.value in options))
              /** fall back */
              factor.value = options["All"]
                ? "All"
                : Object.keys(options)[0] || "";
          },
          { immediate: true },
        ),
      );

      stoppers.push(
        /**
         * when factor value changes, reload data. keep after above so value
         * query reflects fallback.
         */
        watch(factor, loadValues),
      );
    }

    /** immediately run (just once, not duplicate "immediate"s in watches above) */
    loadValues();
  },
  { deep: true },
);

/** is measure a percent */
const percent = computed(() =>
  isPercent(values.value?.min || 0, values.value?.max || 1),
);

/** load map values data */
watch([selectedLevel, selectedCategory, selectedMeasure], loadValues, {
  immediate: true,
});

/** turn facet into list of select box options */
function facetToOptions(facet: Facet): Option[] {
  return Object.values(facet).map(({ id, label }) => ({ id, label }));
}

/** auto-select level option */
watch([levels, selectedLevel], () => {
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

/** location dropdown options */
const locationOptions = computed(() => {
  const entries: Entry[] = [];
  for (const [group, options] of Object.entries(locationGroups)) {
    entries.push({ group });
    for (const option of options) {
      entries.push({
        id: option,
        label: locations.value?.[option]?.label || "",
      });
    }
  }

  return entries;
});

/** location data to pass to map, filtered by selected locations */
const _locations = computed(
  () => pick(locations.value, selectedLocations.value) as Locations | undefined,
);

/** auto-adjust map height */
const map = ref<InstanceType<typeof AppMap>>();
const bounding = computed(() =>
  map.value?.ref ? useElementBounding(map.value.ref) : null,
);
const autoMapHeight = computed(() => {
  if (window.innerHeight < 400) return;
  if (!bounding.value) return;
  if (mapWidth.value || mapHeight.value) return;
  const top = bounding.value.top.value;
  if (top < 0) return;
  return window.innerHeight - top - 40 + "px";
});
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 340px 1fr;
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
  background: var(--gray);
}

.image-preview img {
  width: 100%;
  height: 100%;
  /* center map on particular place (continental US) */
  transform: scale(4.9) translate(28%, 15.4%);
}
</style>
