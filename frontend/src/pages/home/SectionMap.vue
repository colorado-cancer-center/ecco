<template>
  <div class="columns" :style="{ '--cols': mapCols }">
    <!-- left panel -->
    <div class="left-panel" role="group">
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

      <!-- factors -->
      <template v-if="!isEmpty(factors)">
        <div class="factors">
          <template v-for="(factor, index) in factors" :key="index">
            <AppSelect
              v-if="selectedFactors[index]"
              class="factor"
              :model-value="selectedFactors[index]?.value || ''"
              :label="factor.label"
              :options="
                Object.entries(factor.values).map(([key, value]) => ({
                  id: key,
                  label: value,
                }))
              "
              @update:model-value="
                (value) =>
                  (selectedFactors[index]!.value = [value].flat()[0] || '')
              "
            />
          </template>
        </div>
      </template>

      <!-- locations -->
      <AppSelect
        v-model="selectedLocations"
        label="Locations"
        :options="locationOptions"
        :multi="true"
        tooltip="Locations and extra info to show on map, e.g. screening centers, clinics, specialists"
      />

      <!-- multi-map compare -->
      <AppAccordion label="Compare">
        <div class="compare-thumbnails">
          <template v-for="(map, index) in compare" :key="index">
            <!-- eslint-disable-next-line -->
            <AppButton
              v-if="index < compare.length"
              v-tooltip="
                mapsEqual(map, selectedMap)
                  ? `Current map added to comparison. Make new selections above to add another.`
                  : `Remove map from comparison`
              "
              class="compare-thumbnail"
              :icon="faXmark"
              :style="{
                borderColor: mapsEqual(map, selectedMap) ? 'var(--theme)' : '',
              }"
              @click="toggleCompare(map)"
              @mouseenter="highlightedThumbnail = index"
              @mouseleave="highlightedThumbnail = null"
            >
              <img v-if="thumbnails[index]" :src="thumbnails[index]" alt="" />
            </AppButton>
          </template>

          <!-- eslint-disable-next-line -->
          <AppButton
            v-if="!inCompare() && compare.length < maxCompare"
            v-tooltip="`Add current map (selections above) to comparison`"
            class="compare-thumbnail"
            :icon="faPlus"
            @click="toggleCompare()"
            @mouseenter="highlightedThumbnail = thumbnails.length - 1"
            @mouseleave="highlightedThumbnail = null"
          >
            <img
              v-if="thumbnails[thumbnails.length - 1]"
              :src="thumbnails[thumbnails.length - 1]"
              alt=""
              style="opacity: 0.25; filter: saturate(0)"
            />
          </AppButton>
        </div>
      </AppAccordion>

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
                :style="{ scale: flipGradient ? '-1 1' : '' }"
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
      <div
        v-if="renderMap"
        ref="mapGridElement"
        class="map-grid"
        :style="{
          '--width': mapWidth ? `${mapWidth}px` : '',
          '--height': mapHeight ? `${mapHeight}px` : '',

          flexGrow: mapHeight ? '' : 1,
          flexShrink: mapHeight ? 0 : '',
          opacity: mapDataStatus === 'loading' ? 0.5 : 1,
        }"
      >
        <AppMap
          v-for="({ selected, geometry, locations, values }, index) in mapData"
          :key="index"
          ref="mapElement"
          v-model:zoom="zoom"
          v-model:lat="lat"
          v-model:long="long"
          v-model:no-data="noData"
          :style="{
            filter:
              showPreview && compare.length && !inCompare(selected)
                ? 'contrast(0.5) saturate(0) brightness(1.25)'
                : '',
            opacity: index === highlightedThumbnail ? 0.75 : 1,
          }"
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
          @update:thumbnail="(thumb) => (thumbnails[index] = thumb)"
        >
          <!-- main legend -->
          <template #top-left-upper>
            <strong>
              {{
                facets[selected.level]?.list[selected.category]?.list[
                  selected.measure
                ]?.label
              }}
            </strong>
            <div>
              {{ facets[selected.level]?.list[selected.category]?.label }}
            </div>
            <div>
              {{
                Object.values(selected.factors)
                  .filter((factor) => !factor.match(/(^|\s)all($|\s)/i))
                  .join(", ")
              }}
            </div>
          </template>

          <template #top-left-lower>
            <div v-if="values?.source || values?.source_url">
              Source:
              <AppLink :to="values?.source_url ?? ''">
                {{ values?.source ?? "source" }}
              </AppLink>
            </div>
            <div v-if="values?.state">
              State-wide: {{ formatValue(values.state, values.unit) }}
            </div>
          </template>

          <template v-if="countyWide.length" #top-right>
            <b>Outreach (county-level)</b>
            <div class="mini-table">
              <template v-for="(field, index) of countyWide" :key="index">
                <div class="check" :style="{ '--color': field.color }">
                  <font-awesome-icon :icon="faCheck" />
                </div>
                <span>{{ field.label }}</span>
              </template>
            </div>
          </template>

          <!-- geometry feature label -->
          <template
            v-if="countyWide.length"
            #geometry-label="{ feature }: { feature: FeatureInfo }"
          >
            <div>
              <template v-for="(field, index) of countyWide" :key="index">
                <div
                  v-if="field.checkKey && feature[field.checkKey]"
                  class="check"
                  :style="{ '--color': field.color }"
                >
                  <span v-if="field.countKey && feature[field.countKey]">
                    {{ feature[field.countKey] }}
                  </span>
                  <font-awesome-icon v-else :icon="faCheck" />
                </div>
              </template>
            </div>
          </template>

          <!-- feature popup -->
          <template #popup="{ feature }: { feature: FeatureInfo }">
            <!-- main name/identifier -->

            <strong v-if="feature.name">{{ feature.name }}</strong>

            <span v-if="feature.type">{{ feature.type }}</span>

            <strong v-if="feature.fips">
              Census Tract<br />{{ feature.fips }}
            </strong>

            <strong v-if="feature.district">
              District {{ feature.district }}
            </strong>

            <strong v-if="feature.hs_region">
              Health Statistic Region {{ feature.hs_region }}
            </strong>

            <!-- main value -->

            <div class="mini-table">
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

              <template
                v-if="
                  typeof feature.aac === 'number' ||
                  typeof feature.aac === 'string'
                "
              >
                <span>Avg. Annual Count</span>
                <span>{{ formatValue(feature.aac, values?.unit) }}</span>
              </template>

              <template v-if="feature.count">
                <span>Count</span>
                <span>{{ formatValue(feature.count) }}</span>
              </template>
            </div>

            <!-- extra info -->

            <div class="mini-table">
              <template v-if="feature.counties">
                <span>Counties</span>
                <span>
                  <template
                    v-for="(county, index) in feature.counties.split(', ')"
                    :key="index"
                  >
                    {{ county }}<br />
                  </template>
                </span>
              </template>

              <template v-if="feature.org">
                <span>Org</span>
                <span>{{ feature.org }}</span>
              </template>

              <template v-if="typeof feature.link === 'string'">
                <span>Link</span>
                <AppLink :to="feature.link">
                  {{ feature.link.replace(/(https?:\/\/)?(www\.)?/, "") }}
                </AppLink>
              </template>

              <template v-if="feature.representative">
                <span>Representative</span>
                <span>{{ feature.representative }}</span>
              </template>

              <template v-if="feature.party">
                <span>Party</span>
                <span>{{ feature.party }}</span>
              </template>

              <template v-if="feature.email">
                <span>Email</span>
                <span>{{ feature.email }}</span>
              </template>

              <template v-if="feature.address">
                <span>Address</span>
                <span>{{ feature.address }}</span>
              </template>

              <template v-if="feature.phone">
                <span>Phone</span>
                <span>{{ feature.phone }}</span>
              </template>

              <template v-if="feature.notes">
                <span>Notes</span>
                <span>{{ feature.notes }}</span>
              </template>
            </div>

            <!-- outreach -->

            <div v-if="outreachSelected.length" class="mini-table">
              <template v-if="feature.fit_kits">
                <AppLink
                  to="https://medlineplus.gov/ency/patientinstructions/000704.htm"
                >
                  FIT Kits
                </AppLink>
                <span>{{ formatValue(feature.fit_kits) }}</span>
              </template>
              <template v-if="feature.radon_kits">
                <AppLink
                  to="https://cdphe.colorado.gov/hm/testing-your-home-radon"
                >
                  Radon Kits
                </AppLink>
                <span>{{ formatValue(feature.radon_kits) }}</span>
              </template>
              <!-- <template v-if="feature.total_kits">
              <span>Total Kits</span>
              <span>{{ formatValue(feature.total_kits) }}</span>
            </template> -->
              <template v-if="feature.community_events">
                <span>Community Events</span>
                <span>{{ formatValue(feature.community_events) }}</span>
              </template>
              <template v-if="feature.health_fairs">
                <span>Health Fairs</span>
                <span>{{ formatValue(feature.health_fairs) }}</span>
              </template>
              <template v-if="feature.educational_talks">
                <span>Educational Talks</span>
                <span>{{ formatValue(feature.educational_talks) }}</span>
              </template>
              <template v-if="feature.radio_talks">
                <span>Radio Talks</span>
                <span>{{ formatValue(feature.radio_talks) }}</span>
              </template>
              <template v-if="feature.school_church_events">
                <span>School/Church Events</span>
                <span>{{ formatValue(feature.school_church_events) }}</span>
              </template>
              <!-- <template v-if="feature.total_events">
              <span>Total Events</span>
              <span>{{ formatValue(feature.total_events) }}</span>
            </template> -->
              <template v-if="feature.womens_wellness_centers">
                <AppLink to="https://cdphe.colorado.gov/wwc">
                  Women's Wellness Centers
                </AppLink>
                <span>{{ formatValue(feature.womens_wellness_centers) }}</span>
              </template>
              <template v-if="feature['2morrow_signups']">
                <AppLink
                  to="https://medschool.cuanschutz.edu/colorado-cancer-center/community/CommunityOutreachEngagement/projects-and-activities/2morrow-health-app"
                >
                  2morrow Signups
                </AppLink>
                <span>{{ formatValue(feature["2morrow_signups"]) }}</span>
              </template>
            </div>

            <!-- actions -->

            <AppButton
              v-if="selected.level === 'county' && 'county' in feature"
              :icon="faExternalLinkAlt"
              :to="`/county/${feature.id}`"
              :flip="true"
              :new-tab="true"
              >See All</AppButton
            >
          </template>
        </AppMap>
      </div>

      <!-- actions -->
      <div class="row actions">
        <div class="row">
          <AppButton
            v-tooltip="'Download current map(s) view as PNG'"
            :icon="faDownload"
            :accent="true"
            @click="download"
          >
            Map
          </AppButton>
          <AppButton
            v-tooltip="'Zoom out'"
            :icon="faMinus"
            @click="mapElement?.forEach((map) => map?.zoomOut())"
          />
          <AppButton
            v-tooltip="'Zoom in'"
            :icon="faPlus"
            @click="mapElement?.forEach((map) => map?.zoomIn())"
          />
          <AppButton
            v-tooltip="'Fit view to data'"
            :icon="faCropSimple"
            @click="fit"
          >
            Fit
          </AppButton>
          <AppButton
            v-tooltip="'View map(s) in full screen'"
            :icon="faExpand"
            @click="fullscreen"
          >
            Fullscreen
          </AppButton>
        </div>

        <div class="row note">
          <font-awesome-icon :icon="faHandPointer" />Click on a
          {{ selectedLevel }} or location to see more info.
        </div>

        <div class="row">
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
  unref,
  useTemplateRef,
  watch,
  watchEffect,
} from "vue";
import type { ShallowRef, WatchStopHandle } from "vue";
import { toBlob } from "html-to-image";
import {
  clamp,
  cloneDeep,
  isEmpty,
  isEqual,
  mapValues,
  orderBy,
  pick,
  uniqWith,
} from "lodash";
import {
  faComment,
  faHandPointer,
  faQuestionCircle,
} from "@fortawesome/free-regular-svg-icons";
import {
  faArrowRight,
  faArrowsRotate,
  faCheck,
  faCropSimple,
  faDownload,
  faExpand,
  faExternalLinkAlt,
  faFeatherPointed,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons";
import { useElementBounding, useFullscreen, useWindowSize } from "@vueuse/core";
import type {
  Facet,
  Facets,
  GeoProps,
  LocationList,
  LocationProps,
  Values,
} from "@/api";
import {
  extraLocationList,
  getDownload,
  getGeo,
  getLocation,
  getValues,
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
import { colors } from "@/components/markers";
import { backgroundOptions } from "@/components/tile-providers";
import { learnMoreLink } from "@/pages/learn-more";
import {
  arrayParam,
  jsonParam,
  numberParam,
  stringParam,
  useQuery,
  useUrlParam,
} from "@/util/composables";
import { downloadPng } from "@/util/download";
import { formatValue } from "@/util/math";
import { sleep, waitFor } from "@/util/misc";
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

/** map of location id to human-readable label */
const locationLabels = computed(() =>
  Object.fromEntries(
    Object.values(locationList)
      .map((value) => Object.entries(value))
      .flat()
      .map(([label, id]) => [id, label] as const),
  ),
);

/** element refs */
const rightPanelElement = useTemplateRef("rightPanelElement");
const mapGridElement = useTemplateRef("mapGridElement");
const mapElement = useTemplateRef("mapElement");

/** select boxes state */
const selectedLevel = useUrlParam("level", stringParam, "");
const selectedCategory = useUrlParam("category", stringParam, "");
const selectedMeasure = useUrlParam("measure", stringParam, "");
const selectedFactors = shallowRef<Record<string, ShallowRef<string>>>({});
const selectedLocations = useUrlParam("locations", arrayParam(stringParam), []);

/** map zoom state */
const zoom = useUrlParam("zoom", numberParam, 0);
const lat = useUrlParam("lat", numberParam, 0);
const long = useUrlParam("long", numberParam, 0);

/** map style state */
const showLegends = ref(true);
const selectedBackground = ref(backgroundOptions[0]!.id || "");
const selectedGradient = ref(gradientOptions[3]!.id || "");
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
const reset = async () => {
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
};

/** full selected map */
const selectedMap = computed(() => ({
  level: selectedLevel.value,
  category: selectedCategory.value,
  measure: selectedMeasure.value,
  /** unwrap nested refs */
  factors: mapValues(selectedFactors.value, (value) => value.value),
  locations: selectedLocations.value,
}));

type Map = typeof selectedMap.value;

/** show preview of selected map when comparing */
const showPreview = ref(true);

/** map compare group */
const compare = useUrlParam("compare", jsonParam<Map[]>(), []);

/** map thumbnails */
const thumbnails = ref<string[]>([]);

/** highlighted thumbnail */
const highlightedThumbnail = ref<number | null>(null);

/** are two map selections equal */
const mapsEqual = (a: Map, b: Map) =>
  a.level === b.level &&
  a.category === b.category &&
  a.measure === b.measure &&
  Object.entries(a.factors).every(
    ([key, value]) => unref(b.factors[key]) === unref(value),
  ) &&
  isEqual(a.locations, b.locations);

/** is selected map already in compare group */
const inCompare = (map?: Map) => {
  map ??= selectedMap.value;
  return !!compare.value.find((entry) => mapsEqual(map, entry));
};

/** max # of maps that can be compared */
const maxCompare = 9;

/** add/remove selected map from compare group */
const toggleCompare = (map?: Map) => {
  map ??= selectedMap.value;
  if (inCompare(map))
    /** remove */
    compare.value = compare.value.filter((entry) => !mapsEqual(entry, map));
  else if (compare.value.length < maxCompare)
    /** add */
    compare.value.push(map);
};

/** selected map and/or maps in compare group */
const selectedMaps = computed(() =>
  uniqWith(
    [
      /** comparison maps */
      ...compare.value,
      /** selected map */
      ...(showPreview.value || !compare.value.length
        ? [selectedMap.value]
        : []),
    ],
    mapsEqual,
  ),
);

/** load maps data */
const {
  query: loadMapData,
  data: mapData,
  status: mapDataStatus,
} = useQuery(
  () =>
    /** query all maps in parallel */
    Promise.all(
      selectedMaps.value.map(async (selected) => ({
        /** keep input selection */
        selected,

        /** load map geometry data */
        geometry:
          selected.level === "tract"
            ? await getGeo("tracts", "fips")
            : selected.level == "county"
              ? await getGeo("counties", "us_fips")
              : await getGeo("healthregions", "hs_region"),

        /** load map values data */
        values:
          selected.level && selected.category && selected.measure
            ? await getValues(
                selected.level,
                selected.category,
                selected.measure,
                selected.factors,
              )
            : null,

        /** load location data */
        locations: Object.fromEntries(
          /** query for locations in parallel */
          await Promise.all(
            selected.locations
              /** skip locations that shouldn't actually be queried for */
              .filter((entry) => !fakeLocations.value.includes(entry))
              .map(
                async (location) =>
                  [
                    /** location id */
                    locationLabels.value[location] ?? "",
                    /** location geo data */
                    await getLocation(location),
                  ] as const,
              ),
          ),
        ),
      })),
    ),
  [],
  true,
);

/** re-load data when selected maps change */
watch(selectedMaps, loadMapData, { immediate: true, deep: true });

/** how many cols to arrange compare maps in */
const mapCols = computed(() => {
  switch (mapData.value.length) {
    case 1:
      return 1;
    case 2:
    case 4:
      return 2;
    case 3:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
      return 3;
  }
  return 1;
});

/** geographic levels from facets data */
const levels = computed(() => cloneDeep(facets));

/** measure categories from geographic level */
const categories = computed(() =>
  cloneDeep(levels.value[selectedLevel.value]?.list || {}),
);

/** measures from measure category */
const measures = computed(() =>
  cloneDeep(categories.value[selectedCategory.value]?.list || {}),
);

/** turn facet into list of select box options */
const facetToOptions = (facet: Facet): Option[] =>
  Object.values(facet).map(({ id, label }) => ({ id, label }));

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

/**
 * locations that are in location dropdown, but aren't real "locations" in
 * backend and shouldn't be queried for
 */
const fakeLocations = computed<string[]>(() => [
  ...countyWide.value.map(({ id }) => id),
]);

/** are outreach locations selected */
const outreachSelected = computed(() =>
  selectedLocations.value.filter((location) =>
    (
      Object.values(extraLocationList["Outreach and Interventions"]) as string[]
    ).includes(location),
  ),
);

/** county overview outreach data */
const countyWide = computed(() => {
  if (selectedLevel.value !== "county") return [];

  /** get selected overview fields */
  let selected = Object.entries(
    pick(extraLocationList["Outreach and Interventions"], ["2morrow"]),
  )
    .filter(([, id]) => selectedLocations.value.includes(id))
    .map(([label, id]) => ({ id, label }));

  /** preserve selected order */
  selected = orderBy(selected, ({ id }) => selectedLocations.value.indexOf(id));

  /** set field props */
  const fields = selected.map(({ label, id }, index) => ({
    /** actual location "id" (for url, getLocation, etc) */
    id,
    /** key to access on feature to determine if checked or not */
    checkKey: (
      {
        "outreach-2morrow-county": "has_2morrow",
      } satisfies Partial<Record<typeof id, keyof GeoProps>>
    )[id as string],
    /** key to access on feature to determine count */
    countKey: (
      {
        "outreach-2morrow-county": "2morrow_signups",
      } satisfies Partial<Record<typeof id, keyof GeoProps>>
    )[id as string],
    /** human-readable label */
    label,
    /** icon color */
    color: colors[index] ?? "",
  }));

  return fields;
});

/** stratification factors (e.g. race/ethnicity, sex, etc) */
const factors = computed(() =>
  cloneDeep(measures.value[selectedMeasure.value]?.factors || {}),
);

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

watchEffect(() => {
  /** if manual min/max off */
  if (!manualMinMax.value) {
    /** keep in sync with actual min/max (nicer UX when turning manual on) */
    const { min, max } = mapData.value[0]?.values || {};
    if (typeof min === "number") manualMin.value = min;
    if (typeof max === "number") manualMax.value = max;
  }
});

/** fit all maps */
const fit = () => mapElement.value?.forEach((map) => map?.fit());

/** re-fit when col number changes */
watch(mapCols, async () => {
  /** wait for map data to be done loading */
  await waitFor(() => mapDataStatus.value === "success");
  /** wait for map component to render */
  await sleep(10);
  fit();
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

/** download map as png */
const download = async () => {
  if (!mapGridElement.value) return;

  /** convert to image */
  const blob = await toBlob(mapGridElement.value, {
    width: mapWidth.value,
    height: mapHeight.value,
    filter: (node) => {
      if (node instanceof HTMLElement)
        return !node.hasAttribute("data-save-hide");
      return true;
    },
  });

  if (blob) downloadPng(blob, "map");
};

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(mapGridElement);
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
  align-items: center;
  gap: 15px;
}

.compare-thumbnails {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  place-items: center;
  gap: 10px;
}

.compare-thumbnail {
  position: relative;
  aspect-ratio: 2 / 1;
  width: 100%;
  height: 100%;
  padding: 0;
  overflow: hidden;
  border: solid 2px transparent;
}

.compare-thumbnail img {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition:
    opacity var(--fast),
    filter var(--fast);
}

.compare-thumbnail:hover img {
  opacity: 0.25;
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

.map-grid {
  display: grid;
  grid-template-columns: repeat(var(--cols), 1fr);
  width: var(--width);
  height: var(--height);
  gap: 3px;
  background: var(--dark-gray);
  box-shadow: var(--shadow);
  transition: opacity var(--fast);
}

@media (max-width: 800px) {
  .columns {
    grid-template-columns: 1fr;
  }

  .map-grid {
    height: 90vh;
  }
}

.actions {
  gap: 20px;
}

.note {
  flex-grow: 1;
}

.check {
  display: flex;
  align-items: center;
  align-self: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: solid 1px var(--black);
  background: var(--color);
  color: var(--white);
  font-size: 12px;
  -webkit-text-stroke: 2px var(--black);
  paint-order: stroke fill;
}

.check > svg {
  height: 0.75em;
  stroke: currentColor;
  stroke-width: 50px;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
