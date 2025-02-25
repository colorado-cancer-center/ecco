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

      <AppLink :to="learnMoreLink(selectedCategory)" :new-tab="true">
        Learn more about selected data
        <font-awesome-icon :icon="faArrowRight" />
      </AppLink>

      <AppLink
        v-if="selectedLevel === 'tract' || noData"
        to="/sources#suppressed-values"
        :new-tab="true"
      >
        Low values may be suppressed
        <font-awesome-icon :icon="faQuestionCircle" />
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
                      v-for="(color, key) in option?.colors"
                      :key="key"
                      :offset="
                        100 * (key / ((option?.colors.length || 1) - 1)) + '%'
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

        <!-- background layer -->
        <AppSelect
          v-model="selectedBackground"
          label="Background layer"
          :options="backgroundOptions"
          tooltip="Provider to use for background map layer"
        >
          <template #preview="{ option }">
            <div class="image-preview">
              <img :src="option?.image" alt="" />
            </div>
          </template>
        </AppSelect>

        <!-- hide controls that are irrelevant with ordinal unit -->
        <template v-if="values?.unit !== 'ordinal'">
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
        v-model:no-data="noData"
        class="map"
        :style="
          geometryStatus !== 'success' || valuesStatus !== 'success'
            ? { opacity: 0.25, filter: 'saturate(0.25)' }
            : undefined
        "
        :geometry="geometry"
        :locations="locations"
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
        :scale-values="values?.order"
        :width="mapWidth"
        :height="mapHeight"
        :filename="[selectedMeasure, selectedLevel]"
      >
        <!-- main legend -->
        <template #top-left-upper>
          <strong>{{ measures[selectedMeasure]?.label }}</strong>
          <div>{{ categories[selectedCategory]?.label }}</div>
          <div>
            {{
              Object.values(selectedFactors)
                .map((factor) => factor.value)
                .filter((factor) => !factor.match(/(^|\s)all($|\s)/i))
                .join(", ")
            }}
          </div>
          <div v-if="values?.state">State-wide: {{ values?.state }}</div>
        </template>

        <template #top-left-lower>
          <div v-if="values?.source || values?.source_url">
            Source:
            <AppLink :to="values?.source_url ?? ''">
              {{ values?.source ?? "source" }}
            </AppLink>
          </div>
        </template>

        <!-- feature popup -->
        <template #popup="{ feature }: { feature: FeatureInfo }">
          <!-- name -->
          <template v-if="feature.name">
            <strong>{{ feature.name }}</strong>
          </template>

          <!-- id -->
          <template v-if="feature.fips">
            <strong>Census Tract<br />{{ feature.fips }}</strong>
          </template>

          <!-- district -->
          <template v-if="feature.district">
            <strong>District {{ feature.district }}</strong>
          </template>

          <div class="mini-table">
            <!-- primary "value" for feature -->
            <template
              v-if="
                typeof feature.value === 'number' ||
                typeof feature.value === 'string'
              "
            >
              <span>
                {{ feature.aac ? "Rate" : "Value" }}
              </span>
              <span>{{ formatValue(feature.value, values?.unit) }}</span>
            </template>

            <!-- average annual count -->
            <template
              v-if="
                typeof feature.aac === 'number' ||
                typeof feature.aac === 'string'
              "
            >
              <span>Avg. Annual Count</span>
              <span>{{ formatValue(feature.aac, values?.unit) }}</span>
            </template>

            <!-- organization -->
            <template v-if="feature.org">
              <span>Org</span>
              <span>{{ feature.org }}</span>
            </template>

            <!-- link -->
            <template v-if="typeof feature.link === 'string'">
              <span>Link</span>
              <AppLink :to="feature.link">
                {{ feature.link.replace(/(https?:\/\/)?(www\.)?/, "") }}
              </AppLink>
            </template>

            <!-- representative -->
            <template v-if="feature.representative">
              <span>Representative</span>
              <span>{{ feature.representative }}</span>
            </template>

            <!-- party -->
            <template v-if="feature.party">
              <span>Party</span>
              <span>{{ feature.party }}</span>
            </template>

            <!-- email -->
            <template v-if="feature.email">
              <span>Email</span>
              <span>{{ feature.email }}</span>
            </template>

            <!-- address -->
            <template v-if="feature.address">
              <span>Address</span>
              <span>{{ feature.address }}</span>
            </template>

            <!-- phone -->
            <template v-if="feature.phone">
              <span>Phone</span>
              <span>{{ feature.phone }}</span>
            </template>

            <!-- notes -->
            <template v-if="feature.notes">
              <span>Notes</span>
              <span>{{ feature.notes }}</span>
            </template>
          </div>

          <!-- link to full data for county -->
          <AppButton
            v-if="selectedLevel === 'county' && 'county' in feature"
            :icon="faExternalLinkAlt"
            :to="`/county/${feature.id}`"
            :flip="true"
            :new-tab="true"
            >See All Data</AppButton
          >
        </template>
      </AppMap>

      <!-- actions -->
      <div class="actions">
        <div class="action-row">
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
          <AppButton
            v-tooltip="'Zoom in'"
            :icon="faPlus"
            @click="map?.zoomIn"
          />
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

        <div class="action-row note">
          <font-awesome-icon :icon="faHandPointer" />Click on a
          {{ selectedLevel }} or location to see more info.
        </div>

        <div class="action-row">
          <AppButton to="/contact" :icon="faComment" :flip="true" :accent="true"
            >Feedback</AppButton
          >
          <AppButton
            to="/about#acknowledge"
            :icon="faFeatherPointed"
            :flip="true"
            :accent="true"
            >Acknowledge</AppButton
          >
        </div>
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
} from "vue";
import type { ShallowRef, WatchStopHandle } from "vue";
import { clamp, cloneDeep, isEmpty, mapValues } from "lodash";
import {
  faComment,
  faHandPointer,
  faQuestionCircle,
} from "@fortawesome/free-regular-svg-icons";
import {
  faArrowRight,
  faArrowsRotate,
  faCropSimple,
  faDownload,
  faExpand,
  faExternalLinkAlt,
  faFeatherPointed,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons";
import { useElementBounding, useWindowSize } from "@vueuse/core";
import {
  getDownload,
  getGeo,
  getLocation,
  getValues,
  type Facet,
  type Facets,
  type GeoProps,
  type LocationList,
  type LocationProps,
  type Values,
} from "@/api";
import AppAccordion from "@/components/AppAccordion.vue";
import AppButton from "@/components/AppButton.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppLink from "@/components/AppLink.vue";
import AppMap from "@/components/AppMap.vue";
import AppNumber from "@/components/AppNumber.vue";
import AppSelect from "@/components/AppSelect.vue";
import type { Entry, Option } from "@/components/AppSelect.vue";
import AppSlider from "@/components/AppSlider.vue";
import { gradientOptions } from "@/components/gradient";
import { backgroundOptions } from "@/components/tile-providers";
import { learnMoreLink } from "@/pages/learn-more";
import {
  arrayParam,
  numberParam,
  stringParam,
  useQuery,
  useUrlParam,
} from "@/util/composables";
import { formatValue } from "@/util/math";
import { sleep } from "@/util/misc";
import type { Expand, Update } from "@/util/types";

type Props = {
  facets: Facets;
  locationList: LocationList;
};

type Value = NonNullable<Values>["values"][string];

type FeatureInfo = Expand<
  Partial<
    GeoProps &
      LocationProps &
      /** "value" can also be string because of explicit scale */
      Update<Value, "value", string>
  >
>;

const { facets, locationList } = defineProps<Props>();

/** element refs */
const leftPanelElement = ref<HTMLElement>();
const rightPanelElement = ref<HTMLElement>();
const map = ref<InstanceType<typeof AppMap>>();

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
const selectedBackground = ref(backgroundOptions[0]!.id || "");
const selectedGradient = ref(gradientOptions[3]!.id || "");
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
  selectedBackground.value = backgroundOptions[0]?.id || "";
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

/** load geometry data to display on map */
const {
  query: loadGeometry,
  data: geometry,
  status: geometryStatus,
} = useQuery(async function () {
  if (selectedLevel.value === "county")
    return await getGeo("counties", "us_fips");
  else if (selectedLevel.value === "tract")
    return await getGeo("tracts", "fips");
}, undefined);

/** load geometry data to display on map */
watch(selectedLevel, loadGeometry, { immediate: true });

/** geographic levels from facets data */
const levels = computed(() => cloneDeep(facets));

/** measure categories from geographic level */
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.list || {}),
);

const {
  query: loadValues,
  data: values,
  status: valuesStatus,
} = useQuery(
  /** load map values data */
  async function () {
    if (
      !selectedLevel.value ||
      !selectedCategory.value ||
      !selectedMeasure.value
    )
      return;
    return await getValues(
      selectedLevel.value,
      selectedCategory.value,
      selectedMeasure.value,
      /** unwrap nested refs */
      mapValues(selectedFactors.value, (value) => value.value),
    );
  },
  undefined,
);

/** measures from measure category */
const measures = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.list || {}),
);

/** stratification factors (e.g. race/ethnicity, sex, etc) */
const factors = computed(() =>
  cloneDeep(measures.value[selectedMeasure.value]?.factors || {}),
);

/** selected value state for each factor */
const selectedFactors = shallowRef<Record<string, ShallowRef<string>>>({});

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
      /** default fallback option */
      const fallback =
        value.default in value.values
          ? /** explicitly defined default */
            value.default
          : /** first option */
            Object.entries(value.values || {})[0]?.[0] || "";

      /** ref 2-way synced with url */
      const factor = useUrlParam(key, stringParam, fallback);
      /** hook up url reactive with selected factor */
      selectedFactors.value[key] = factor;

      /** dynamically create watcher for factor */
      stoppers.push(
        /** when factor value changes */
        watch(
          factor,
          () => {
            /** get non-stale factor options */
            const newValue = factors.value[key];
            /** if value isn't valid anymore */
            if (!(factor.value in (newValue?.values || {})))
              /** fall back */
              factor.value = fallback;
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
  for (const [group, options] of Object.entries(locationList)) {
    entries.push({ group });
    for (const [label, id] of Object.entries(options))
      entries.push({ id, label });
  }

  return entries;
});

/** get location data to pass to map based on selected locations */
const { query: loadLocations, data: locations } = useQuery(
  async function () {
    /** convert locations list to map of id to human-readable label */
    const idToLabel = Object.fromEntries(
      Object.values(locationList)
        .map((value) => Object.entries(value))
        .flat()
        .map(([label, id]) => [id, label] as const),
    );

    return Object.fromEntries(
      /** query for locations in parallel */
      await Promise.all(
        selectedLocations.value.map(
          async (location) =>
            [
              /** location id */
              idToLabel[location] ?? "",
              /** location geo data */
              await getLocation(location),
            ] as const,
        ),
      ),
    );
  },
  undefined,
  true,
);
watch(selectedLocations, loadLocations, { immediate: true });

watchEffect(() => {
  /** if manual min/max off */
  if (!manualMinMax.value) {
    /** keep in sync with actual min/max (nicer UX when turning manual on) */
    const { min, max } = values.value || {};
    if (typeof min === "number") manualMin.value = min;
    if (typeof max === "number") manualMax.value = max;
  }
});

/** auto-adjust right panel/map height */
const autoRightPanelHeight = ref("");
const { top: rightPanelTop } = useElementBounding(rightPanelElement);
const { height: windowHeight } = useWindowSize();
watch(
  [rightPanelTop, windowHeight],
  () => {
    if (windowHeight.value < 400) return;
    if (!rightPanelTop.value) return;
    if (mapWidth.value || mapHeight.value) return;
    const top = rightPanelTop.value;
    const max = windowHeight.value - 20;
    autoRightPanelHeight.value = clamp(max - top, 400, max) + "px";
  },
  { immediate: true },
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
  translate: 140% 70%;
  scale: 5;
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
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.action-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.note {
  flex-grow: 1;
}
</style>
