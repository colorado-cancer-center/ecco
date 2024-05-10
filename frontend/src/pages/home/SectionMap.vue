<template>
  <div class="columns">
    <!-- left panel -->
    <div ref="leftPanelElement" class="left-panel" role="group">
      <!-- data selections -->
      <AppSelect
        v-model="selectedLevel"
        label="Geographic level"
        :options="facetToOptions(levels)"
      />

      <AppLink
        v-if="selectedLevel === 'tract'"
        to="/sources#suppressed-values"
        :new-tab="true"
      >
        <font-awesome-icon :icon="faQuestionCircle" class="icon" />
        Low values may be suppressed
      </AppLink>

      <div class="side-control">
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
        />
      </div>

      <div class="side-control">
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
        />
      </div>

      <AppLink :to="learnMoreLink" :new-tab="true">
        <font-awesome-icon :icon="faQuestionCircle" class="icon" />
        Learn more about selected data
      </AppLink>

      <hr />

      <!-- factors -->
      <template v-if="!isEmpty(factors)">
        <div class="factors">
          <template v-for="(factor, key) in factors" :key="key">
            <AppSelect
              v-if="selectedFactors[key]"
              class="factor"
              :model-value="selectedFactors[key]?.value || ''"
              :label="factor.label"
              :options="
                Object.entries(factor.values).map(([key, value]) => ({
                  id: key,
                  label: value,
                }))
              "
              @update:model-value="
                (value) =>
                  (selectedFactors[key]!.value = [value].flat()[0] || '')
              "
            />
          </template>
        </div>

        <hr />
      </template>

      <!-- locations -->
      <AppSelect
        v-model="selectedLocations"
        label="Locations"
        :options="locationOptions"
        :multi="true"
        tooltip="Locations to show on map, e.g. screening centers, clinics,
      specialists"
      />

      <hr />

      <AppAccordion label="Customization">
        <!-- legend -->
        <div class="control-row">
          <AppCheckbox
            v-model="showLegends"
            v-tooltip="'Show/hide legend panels on map'"
            label="Show legends"
          />
          <AppCheckbox
            v-model="showExtras"
            v-tooltip="'Show/hide extra info in legends'"
            label="Extra info"
          />
        </div>

        <!-- gradient -->
        <div class="side-control">
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
            label="Flip"
          />
        </div>

        <!-- base layer -->
        <AppSelect
          v-model="selectedBackground"
          label="Background layer"
          :options="baseOptions"
          tooltip="Provider to use for background map layer"
        >
          <template #preview="{ option }">
            <div class="image-preview">
              <img :src="option?.image" alt="" />
            </div>
          </template>
        </AppSelect>

        <!-- hide controls that are irrelevant with explicit scale -->
        <template v-if="!values?.explicitScale">
          <div class="control-row">
            <!-- scale min/max -->
            <AppCheckbox
              v-model="manualMinMax"
              v-tooltip="'Manually set scale min/max'"
              label="Manual min/max"
            />
            <template v-if="manualMinMax">
              <AppNumber
                v-model="manualMin"
                v-tooltip="'Manual scale min'"
                :min="-Infinity"
                :max="Infinity"
                :step="0.01"
                label="Min"
              />
              <AppNumber
                v-model="manualMax"
                v-tooltip="'Manual scale max'"
                :min="-Infinity"
                :max="Infinity"
                :step="0.01"
                label="Max"
              />
            </template>
          </div>

          <!-- scale steps -->
          <div class="control-row">
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

            <AppCheckbox
              v-model="niceSteps"
              v-tooltip="
                'Adjust number of scale steps to get nice, round intervals (when power = 1)'
              "
              label="Nice steps"
            />
          </div>
        </template>

        <!-- layer opacities -->
        <div class="control-row">
          <AppSlider
            v-model="backgroundOpacity"
            v-tooltip="'Transparency of background layer'"
            label="Bg. trans."
          />

          <AppSlider
            v-model="geometryOpacity"
            v-tooltip="'Transparency of geometry layer'"
            label="Geom. trans."
          />

          <AppSlider
            v-model="locationOpacity"
            v-tooltip="'Transparency of selected locations layer'"
            label="Loc. trans."
          />
        </div>

        <!-- dimensions -->
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

        <!-- reset -->
        <AppButton
          v-tooltip="'Reset customizations and map to defaults'"
          :icon="faArrowsRotate"
          :accent="true"
          @click="reset"
          >Reset</AppButton
        >
      </AppAccordion>
    </div>

    <!-- right panel -->
    <div
      ref="rightPanelElement"
      class="right-panel"
      :style="{ height: autoRightPanelHeight }"
    >
      <!-- map -->
      <AppMap
        v-if="renderMap"
        ref="map"
        v-model:zoom="zoom"
        v-model:lat="lat"
        v-model:long="long"
        class="map"
        :style="
          geometryStatus !== 'success' || valuesStatus !== 'success'
            ? {
                opacity: 0.25,
                filter: 'saturate(0.25)',
              }
            : null
        "
        :geometry="geometry"
        :locations="filteredLocations"
        :values="values?.values"
        :min="manualMinMax ? manualMin : values?.min"
        :max="manualMinMax ? manualMax : values?.max"
        :unit="values?.unit"
        :show-legends="showLegends"
        :background-opacity="backgroundOpacity"
        :geometry-opacity="geometryOpacity"
        :location-opacity="locationOpacity"
        :background="selectedBackground"
        :gradient="selectedGradient"
        :flip-gradient="flipGradient"
        :scale-steps="scaleSteps"
        :nice-steps="niceSteps"
        :scale-power="scalePower"
        :explicit-scale="values?.explicitScale"
        :width="mapWidth"
        :height="mapHeight"
        :filename="[selectedMeasure, selectedLevel]"
        @no-data="(value) => (noData = value)"
      >
        <!-- main legend -->
        <template #top-left>
          <div>
            <strong>{{ measures[selectedMeasure]?.label }}</strong>
            <br />
            {{ categories[selectedCategory]?.label }}
            <br />
            by {{ levels[selectedLevel]?.label }}
            <br />
          </div>
        </template>

        <!-- selected factors -->
        <template v-if="showExtras && !isEmpty(factors)" #top-right>
          <div class="mini-table">
            <template v-for="(factor, key) in factors" :key="key">
              <span>{{ factor.label }}</span>
              <span>{{
                factor.values[selectedFactors[key]?.value || ""]
              }}</span>
            </template>
          </div>
        </template>

        <!-- stats -->
        <template v-if="showExtras && values" #bottom-left>
          <div class="mini-table">
            <template v-for="(stat, index) in stats" :key="index">
              <span v-tooltip="startCase(values.unit ?? '')">
                {{ stat.key }}
              </span>
              <span v-tooltip="stat.full">
                {{ stat.compact }}
              </span>
            </template>
          </div>
        </template>
      </AppMap>

      <!-- actions -->
      <div class="actions">
        <AppButton
          v-tooltip="'Download current map view as PNG'"
          :icon="faDownload"
          :accent="true"
          @click="map?.download"
        >
          Map
        </AppButton>
        <AppButton
          v-tooltip="'Zoom out'"
          :icon="faMinus"
          @click="map?.zoomOut"
        />
        <AppButton v-tooltip="'Zoom in'" :icon="faPlus" @click="map?.zoomIn" />
        <AppButton
          v-tooltip="'Fit view to data'"
          :icon="faCropSimple"
          @click="map?.fit"
        >
          Fit
        </AppButton>
        <AppButton
          v-tooltip="'View map in full screen'"
          :icon="faExpand"
          @click="map?.fullscreen"
        >
          Fullscreen
        </AppButton>
      </div>
    </div>
  </div>
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
import { clamp, cloneDeep, isEmpty, mapValues, pick, startCase } from "lodash";
import { faQuestionCircle } from "@fortawesome/free-regular-svg-icons";
import {
  faArrowsRotate,
  faCropSimple,
  faDownload,
  faExpand,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons";
import { debouncedWatch, useElementBounding } from "@vueuse/core";
import {
  getDownload,
  getGeo,
  getValues,
  type Data,
  type Facet,
  type Facets,
  type Locations,
  type Values,
} from "@/api";
import locationGroups from "@/api/location-groups.json";
import AppAccordion from "@/components/AppAccordion.vue";
import AppButton from "@/components/AppButton.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppLink from "@/components/AppLink.vue";
import AppMap from "@/components/AppMap.vue";
import AppNumber from "@/components/AppNumber.vue";
import AppSelect, { type Entry, type Option } from "@/components/AppSelect.vue";
import AppSlider from "@/components/AppSlider.vue";
import { type Status } from "@/components/AppStatus.vue";
import { gradientOptions } from "@/components/gradient";
import { baseOptions } from "@/components/tile-providers";
import {
  arrayParam,
  numberParam,
  stringParam,
  useUrlParam,
} from "@/util/composables";
import { formatValue } from "@/util/math";
import { sleep } from "@/util/misc";

type Props = {
  facets: Facets;
  locations: Locations;
};

/** list of measure stats */
const stats = computed(() =>
  values.value
    ? (["min", "max", "mean", "median"] as const).map((key) => ({
        key: startCase(key),
        full: formatValue(values.value![key], values.value!.unit),
        compact: formatValue(values.value![key], values.value!.unit, true),
      }))
    : [],
);

const props = defineProps<Props>();

/** element refs */
const leftPanelElement = ref<HTMLElement>();
const rightPanelElement = ref<HTMLElement>();
const map = ref<InstanceType<typeof AppMap>>();

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

/** data state */
const geometryStatus = ref<Status>("loading");
const counties = ref<Data>();
const tracts = ref<Data>();
const geometry = ref<Data>();
const valuesStatus = ref<Status>("loading");
const values = ref<Values>();

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
const showExtras = ref(false);
const selectedBackground = ref(baseOptions[0]?.id || "");
const selectedGradient = ref(gradientOptions[3]?.id || "");
const selectedLocations = useUrlParam("locations", arrayParam(stringParam), []);
const backgroundOpacity = ref(1);
const geometryOpacity = ref(0.75);
const locationOpacity = ref(1);
const flipGradient = ref(false);
const scaleSteps = ref(5);
const niceSteps = ref(false);
const scalePower = ref(1);
const manualMinMax = ref(false);
const manualMin = ref(0);
const manualMax = ref(1);
const mapWidth = ref(0);
const mapHeight = ref(0);

/** whether map has any "no data" regions */
const noData = ref(false);

/** flag to force rerender of map */
const renderMap = ref(true);

/** reset customizations and map to defaults */
async function reset() {
  zoom.value = 0;
  lat.value = 0;
  long.value = 0;
  showLegends.value = true;
  showExtras.value = false;
  selectedBackground.value = baseOptions[0]?.id || "";
  selectedGradient.value = gradientOptions[3]?.id || "";
  backgroundOpacity.value = 1;
  geometryOpacity.value = 0.75;
  locationOpacity.value = 1;
  flipGradient.value = false;
  scaleSteps.value = 6;
  niceSteps.value = false;
  scalePower.value = 1;
  manualMinMax.value = false;
  mapWidth.value = 0;
  mapHeight.value = 0;

  /**
   * force full re-render of map. don't do this via key method to make sure
   * entire dom completely unmounted and recreated from scratch (no diffing by
   * vue)
   */
  renderMap.value = false;
  await sleep(100);
  renderMap.value = true;
}

/** load and select geometry data to display on map, on request to save bandwidth */
watchEffect(async () => {
  try {
    geometryStatus.value = "loading";
    /** clear geometry while loading */
    geometry.value = undefined;

    /** choose and fetch data */
    if (selectedLevel.value === "county") {
      counties.value ??= await getGeo("counties", "us_fips");
      geometry.value = counties.value;
    } else if (selectedLevel.value === "tract") {
      tracts.value ??= await getGeo("tracts", "fips");
      geometry.value = tracts.value;
    }

    geometryStatus.value = "success";
  } catch (error) {
    console.error(error);
    geometryStatus.value = "error";
  }
});

/** geographic levels from facets data */
const levels = computed(() => cloneDeep(props.facets));

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

  valuesStatus.value = "loading";
  /** clear values while loading */
  values.value = undefined;

  /** assign unique id to query */
  latest = Symbol();
  const current = latest;

  try {
    /** fetch data */
    const result = await getValues(
      selectedLevel.value,
      selectedCategory.value,
      selectedMeasure.value,
      /** unwrap nested refs */
      mapValues(selectedFactors.value, (value) => value.value),
    );

    /** check if current query is latest (prevent race conditions) */
    if (current === latest) values.value = result;
    else console.debug("stale");

    valuesStatus.value = "success";
  } catch (error) {
    console.error(error);
    valuesStatus.value = "error";
  }
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
    /** reset selected factors */
    selectedFactors.value = {};

    /** all previous watchers irrelevant now */
    clearFactorWatchers();

    /** for each factor */
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

      /** dynamically create watcher for factor */
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
    }
  },
  { immediate: true, deep: true },
);

/** load map values data */
watch(
  [selectedLevel, selectedCategory, selectedMeasure, selectedFactors],
  loadValues,
  { deep: true, immediate: true },
);

/** turn facet into list of select box options */
function facetToOptions(facet: Facet): Option[] {
  return Object.values(facet).map(({ id, label }) => ({ id, label }));
}

/** auto-select level option */
watch(
  [levels, selectedLevel],
  () => {
    /** if not already selected, or selection no longer valid */
    if (!selectedLevel.value || !levels.value[selectedLevel.value])
      selectedLevel.value = Object.keys(levels.value)[0] || "";
  },
  { immediate: true },
);

/** auto-select category */
watch(
  [selectedLevel, categories],
  () => {
    if (!selectedCategory.value || !categories.value[selectedCategory.value])
      selectedCategory.value = categories.value["sociodemographics"]
        ? "sociodemographics"
        : Object.keys(categories.value)[0] || "";
  },
  { immediate: true },
);

/** auto-select measure */
watch(
  [selectedCategory, measures],
  () => {
    if (!selectedMeasure.value || !measures.value[selectedMeasure.value])
      selectedMeasure.value = measures.value["Total"]
        ? "Total"
        : Object.keys(measures.value)[0] || "";
  },
  { immediate: true },
);

/** location dropdown options */
const locationOptions = computed(() => {
  const entries: Entry[] = [];
  for (const [group, options] of Object.entries(locationGroups)) {
    entries.push({ group });
    for (const option of options) {
      entries.push({
        id: option,
        label: props.locations[option]?.label || "",
      });
    }
  }

  return entries;
});

/** location data to pass to map, filtered by selected locations */
const filteredLocations = computed(
  () => pick(props.locations, selectedLocations.value) as Locations | undefined,
);

watchEffect(() => {
  /** if manual min/max off */
  if (!manualMinMax.value) {
    /** keep in sync with actual min/max (nicer UX when turning manual on) */
    const { min, max } = values.value || {};
    if (min !== undefined) manualMin.value = min;
    if (max !== undefined) manualMax.value = max;
  }
});

/** auto-adjust right panel/map height */
const autoRightPanelHeight = ref("");
const rightPanelBbox = computed(() =>
  rightPanelElement.value ? useElementBounding(rightPanelElement.value) : null,
);
debouncedWatch(
  rightPanelBbox,
  () => {
    if (window.innerHeight < 400) return;
    if (!rightPanelBbox.value) return;
    if (mapWidth.value || mapHeight.value) return;
    const top = rightPanelBbox.value.top.value;
    const max = window.innerHeight - 20;
    autoRightPanelHeight.value = clamp(max - top, 400, max) + "px";
  },
  {
    deep: true,
    /** avoid browser slow-down */
    debounce: 500,
  },
);
</script>

<style scoped>
.columns {
  display: grid;
  grid-template-columns: 360px 1fr;
  margin: 40px 0;
  gap: 40px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.factors {
  display: grid;
  grid-template-columns: min-content 1fr;
  align-items: center;
  gap: 10px;
}

.factor {
  display: contents;
}

.side-control {
  display: grid;
  grid-template-columns: 1fr min-content;
  align-items: flex-end;
  gap: 10px;
}

.control-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  align-items: flex-end;
  gap: 15px;
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
  gap: 10px;
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

.right-panel {
  display: flex;
  position: sticky;
  top: 20px;
  flex-direction: column;
  align-items: stretch;
  min-width: 0;
  min-height: 0;
  gap: 20px;
}

:deep(.map) {
  flex-grow: 1;
  transition: opacity var(--fast);
}

@media (max-width: 800px) {
  .columns {
    grid-template-columns: 1fr;
  }

  .map {
    height: 90vh;
  }
}

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 10px;
}
</style>
