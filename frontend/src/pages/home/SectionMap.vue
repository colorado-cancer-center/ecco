<template>
  <div
    class="grid grid-cols-[--spacing(100)_1fr] gap-8 max-md:grid-cols-1"
    :style="{ '--cols': mapCols }"
  >
    <!-- left panel -->
    <div class="flex flex-col gap-8 text-left" role="group">
      <!-- geographic level -->
      <AppSelect
        v-model="selectedMap().level"
        :options="levelOptions"
        label="Geographic level"
        :class="[levelStatus === 'loading' && 'animate-pulse']"
      />

      <!-- statistics -->
      <AppTree
        v-model="selectedMap().statistic"
        :tree="statisticOptions"
        :class="[statisticStatus === 'loading' && 'animate-pulse']"
      >
        <template #default="{ child }">
          <AppButton
            v-if="child.id"
            v-tooltip="'Download statistic data'"
            :to="onTreeDownload(child.id)"
            class="size-8 min-h-0! min-w-0! rounded-md bg-transparent text-stone-300 hover:text-black"
          >
            <Download />
          </AppButton>
        </template>
      </AppTree>

      <!-- locations -->
      <AppSelect
        v-model="selectedMap().locations"
        multi
        :options="locationOptions"
        label="Resources & Other Locations"
        :class="[locationsStatus === 'loading' && 'animate-pulse']"
      />

      <AppCollapsible label="Customization">
        <!-- legend -->
        <AppCheckbox
          v-model="showLegends"
          v-tooltip="'Show/hide legend panels on map'"
          label="Show legends"
        />

        <!-- gradient -->
        <div class="grid grid-cols-[1fr_min-content] items-end gap-2">
          <AppSelect
            v-model="selectedGradient"
            v-tooltip="'Gradient to use for coloring map data'"
            label="Gradient"
            :options="gradientOptions"
            :truncate="true"
          >
            <template #preview="{ option }">
              <svg
                :viewBox="`0 0 10 1`"
                preserveAspectRatio="none"
                class="h-6 w-12"
                :class="flipGradient && '-scale-x-100'"
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
            <div class="size-12 shrink-0 overflow-hidden bg-stone-300">
              <img
                :src="option?.image"
                alt=""
                class="size-full translate-x-14/10 translate-y-7/10 scale-500"
              />
            </div>
          </template>
        </AppSelect>

        <!-- scale min/max -->
        <AppCheckbox
          v-model="manualMinMax"
          v-tooltip="'Manually set scale min/max'"
          label="Manual min/max"
        />
        <div v-if="manualMinMax" class="grid grid-cols-2 gap-2">
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
        </div>

        <!-- scale steps -->
        <div class="grid grid-cols-2 gap-2">
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
        <AppCheckbox
          v-model="niceSteps"
          v-tooltip="
            'Adjust number of scale steps to get nice, round intervals (when power = 1)'
          "
          label="Nice steps"
        />

        <!-- layer opacities -->
        <AppSlider
          v-model="backgroundOpacity"
          v-tooltip="'Transparency of background layer'"
          label="Background transparency"
        />
        <AppSlider
          v-model="geographyOpacity"
          v-tooltip="'Transparency of geography layer'"
          label="Geography transparency"
        />
        <AppSlider
          v-model="locationOpacity"
          v-tooltip="'Transparency of resources & locations layer'"
          label="Locations transparency"
        />

        <!-- dimensions -->
        <label
          v-tooltip="
            'Exact dimensions of map. Useful to set before downloading as image. Leave as 0 to fit to page.'
          "
          class="flex cursor-pointer flex-col items-stretch gap-1"
        >
          <span>Map dimensions</span>
          <div class="grid grid-cols-[1fr_min-content_1fr] items-center gap-2">
            <AppNumber
              v-model="mapWidth"
              label="Map width"
              :hide-label="true"
              :max="2000"
              :step="100"
            />
            <span>&times;</span>
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
          v-tooltip="'Reset customizations to defaults'"
          :accent="true"
          @click="reset"
        >
          <RefreshCw />
          Reset
        </AppButton>
      </AppCollapsible>
    </div>

    <!-- right panel -->
    <div
      ref="rightPanelElement"
      class="sticky top-4 flex min-h-0 min-w-0 flex-col items-stretch gap-4"
      :style="{ height: autoRightPanelHeight + 'px' }"
    >
      <!-- map -->
      <div
        ref="mapGridElement"
        class="grid h-(--height) w-(--width) grid-cols-[repeat(var(--cols),1fr)] gap-1 bg-stone-600 shadow-md transition max-md:h-[90dvh]"
        :class="[
          mapDataStatus === 'loading' && 'animate-pulse',
          mapHeight ? 'shrink-0' : 'grow',
        ]"
        :style="{
          '--width': mapWidth ? `${mapWidth}px` : '',
          '--height': mapHeight ? `${mapHeight}px` : '',
        }"
      >
        <AppMap
          v-for="(
            { selected, geography, statistic, locations }, index
          ) in mapData"
          :key="index"
          ref="mapElement"
          v-model:zoom="zoom"
          v-model:lat="lat"
          v-model:long="long"
          :geography="geography"
          :locations="locations"
          :min="manualMinMax ? manualMin : statistic.min"
          :max="manualMinMax ? manualMax : statistic.max"
          :unit="statistic.unit"
          :show-legends="showLegends"
          :background-opacity="backgroundOpacity"
          :geography-opacity="geographyOpacity"
          :location-opacity="locationOpacity"
          :background="selectedBackground"
          :gradient="selectedGradient"
          :flip-gradient="flipGradient"
          :scale-steps="scaleSteps"
          :nice-steps="niceSteps"
          :scale-power="scalePower"
          :scale-values="statistic.order"
        >
          <!-- main legend -->
          <template #top-left-upper> </template>

          <template #top-left-lower>
            <div v-if="statistic.source" class="flex items-center gap-2">
              <AppLink :to="statistic.source.link">
                {{ statistic.source.label }}
              </AppLink>
              <AppButton
                v-tooltip="'Copy citation text to clipboard'"
                class="min-h-0! min-w-0! p-1!"
                data-save-hide
                @click="copy(getSourceCitation(statistic.source))"
              >
                <Copy />
              </AppButton>
            </div>

            <div v-if="statistic.state">
              State-wide: {{ formatValue(statistic.state, statistic.unit) }}
            </div>
          </template>

          <!-- feature popup -->
          <template #popup="{ feature }">
            <!-- main name/identifier -->

            <strong v-if="feature.label">
              {{ feature.label }}
            </strong>

            <strong v-if="feature.district">
              District {{ feature.district }}
            </strong>

            <dl>
              <!-- main values -->

              <template
                v-if="
                  typeof feature.value === 'number' ||
                  typeof feature.value === 'string'
                "
              >
                <dt>
                  {{ feature.aac ? "Rate" : "Value" }}
                </dt>
                <dd>
                  {{ formatValue(feature.value, statistic.unit) }}
                </dd>
              </template>

              <template
                v-if="
                  typeof feature.aac === 'number' ||
                  typeof feature.aac === 'string'
                "
              >
                <dt>Avg. Annual Count</dt>
                <dd>{{ formatValue(feature.aac, statistic.unit) }}</dd>
              </template>

              <template v-if="feature.count">
                <dt>Count</dt>
                <dd>{{ formatValue(feature.count) }}</dd>
              </template>

              <!-- extra info -->

              <template v-if="feature.description">
                <dt>Description</dt>
                <dd>
                  {{ feature.description }}
                </dd>
              </template>

              <template v-if="feature.org">
                <dt>Org</dt>
                <dd>{{ feature.org }}</dd>
              </template>

              <template v-if="typeof feature.link === 'string'">
                <dt>Link</dt>
                <dd>
                  <AppLink :to="feature.link">
                    {{ feature.link.replace(/(https?:\/\/)?(www\.)?/, "") }}
                  </AppLink>
                </dd>
              </template>

              <template v-if="feature.zip_code">
                <dt>ZIP Code</dt>
                <dd>{{ feature.zip_code }}</dd>
              </template>

              <template v-if="feature.area_type">
                <dt>Area Type</dt>
                <dd>{{ feature.area_type }}</dd>
              </template>

              <template v-if="feature.representative">
                <dt>Representative</dt>
                <dd>{{ feature.representative }}</dd>
              </template>

              <template v-if="feature.party">
                <dt>Party</dt>
                <dd>{{ feature.party }}</dd>
              </template>

              <template v-if="feature.email">
                <dt>Email</dt>
                <dd>{{ feature.email }}</dd>
              </template>

              <template v-if="feature.address">
                <dt>Address</dt>
                <dd>{{ feature.address }}</dd>
              </template>

              <template v-if="feature.phone">
                <dt>Phone</dt>
                <dd>{{ feature.phone }}</dd>
              </template>

              <template v-if="feature.notes">
                <dt>Notes</dt>
                <dd>{{ feature.notes }}</dd>
              </template>

              <!-- outreach -->

              <template v-if="feature.fit_kits">
                <dt>
                  <AppLink
                    to="https://medlineplus.gov/ency/patientinstructions/000704.htm"
                  >
                    FIT Kits
                  </AppLink>
                </dt>
                <dd>{{ formatValue(feature.fit_kits) }}</dd>
              </template>

              <template v-if="feature.radon_kits">
                <dt>
                  <AppLink
                    to="https://cdphe.colorado.gov/hm/testing-your-home-radon"
                  >
                    Radon Kits
                  </AppLink>
                </dt>
                <dd>{{ formatValue(feature.radon_kits) }}</dd>
              </template>

              <template v-if="feature.community_events">
                <dt>Community Events</dt>
                <dd>{{ formatValue(feature.community_events) }}</dd>
              </template>

              <template v-if="feature.health_fairs">
                <dt>Health Fairs</dt>
                <dd>{{ formatValue(feature.health_fairs) }}</dd>
              </template>

              <template v-if="feature.educational_talks">
                <dt>Educational Talks</dt>
                <dd>{{ formatValue(feature.educational_talks) }}</dd>
              </template>

              <template v-if="feature.radio_talks">
                <dt>Radio Talks</dt>
                <dd>{{ formatValue(feature.radio_talks) }}</dd>
              </template>

              <template v-if="feature.school_church_events">
                <dt>School/Church Events</dt>
                <dd>{{ formatValue(feature.school_church_events) }}</dd>
              </template>

              <template v-if="feature.womens_wellness_centers">
                <dt>
                  <AppLink to="https://cdphe.colorado.gov/wwc">
                    Women's Wellness Centers
                  </AppLink>
                </dt>
                <dd>{{ formatValue(feature.womens_wellness_centers) }}</dd>
              </template>

              <template v-if="feature['2morrow_signups']">
                <dt>
                  <AppLink
                    to="https://medschool.cuanschutz.edu/colorado-cancer-center/community/CommunityOutreachEngagement/projects-and-activities/2morrow-health-app"
                  >
                    2morrow Signups
                  </AppLink>
                </dt>
                <dd>{{ formatValue(feature["2morrow_signups"]) }}</dd>
              </template>
            </dl>

            <!-- actions -->
            <AppButton
              v-if="selected.level === 'county'"
              :to="`/county/${feature.id}`"
              :new-tab="true"
            >
              All county data
            </AppButton>
          </template>
        </AppMap>
      </div>

      <!-- actions -->
      <div class="flex flex-wrap items-center justify-center gap-4">
        <div class="flex flex-wrap items-center justify-center gap-2">
          <AppButton
            v-tooltip="'Download map(s) as PNG'"
            :accent="true"
            @click="downloadMapImage"
          >
            <Download />
            Map
          </AppButton>
          <AppButton
            v-tooltip="'Download map(s) as GeoJSON'"
            @click="downloadMapGeo"
          >
            <Download />
            Geo
          </AppButton>
          <AppButton
            v-tooltip="'Zoom out'"
            @click="mapElement?.forEach((map) => map?.zoomOut())"
          >
            <Minus />
          </AppButton>
          <AppButton
            v-tooltip="'Zoom in'"
            @click="mapElement?.forEach((map) => map?.zoomIn())"
          >
            <Plus />
          </AppButton>
          <AppButton v-tooltip="'Fit view to data'" @click="fit">
            <Crop />
            Fit
          </AppButton>
          <AppButton
            v-tooltip="'View map(s) in full screen'"
            @click="fullscreen"
          >
            <Fullscreen />
            Fullscreen
          </AppButton>
        </div>

        <div class="flex grow flex-wrap items-center justify-center gap-2">
          <Pointer />Try interacting with the map
        </div>

        <div class="flex flex-wrap items-center justify-center gap-2">
          <AppButton to="/contact" :accent="true">
            Feedback
            <MessageCircle />
          </AppButton>
          <AppButton to="/about#acknowledge" :accent="true">
            Acknowledge
            <Feather />
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Tree } from "@/components/AppTree.vue";
import {
  computed,
  onMounted,
  ref,
  useTemplateRef,
  watch,
  watchEffect,
} from "vue";
import {
  getDownload,
  getLevel,
  getLevels,
  getLocation,
  getLocations,
  getSourceCitation,
  getStatistic,
  getStatistics,
} from "@/api";
import locationGroups from "@/api/data/location-groups.json";
import statisticGroups from "@/api/data/statistic-groups.json";
import AppButton from "@/components/AppButton.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppCollapsible from "@/components/AppCollapsible.vue";
import AppLink from "@/components/AppLink.vue";
import AppMap from "@/components/AppMap.vue";
import AppNumber from "@/components/AppNumber.vue";
import AppSelect from "@/components/AppSelect.vue";
import AppSlider from "@/components/AppSlider.vue";
import AppTree from "@/components/AppTree.vue";
import { backgroundOptions, defaultBackground } from "@/components/background";
import { defaultGradient, gradientOptions } from "@/components/gradient";
import { appTitle } from "@/meta";
import { numberParam, useDeepRouteQuery } from "@/pages";
import { useQuery } from "@/util/composables";
import { downloadJson, downloadPng } from "@/util/download";
import { formatValue } from "@/util/math";
import { copy } from "@/util/misc";
import { getValue } from "@/util/types";
import {
  Copy,
  Crop,
  Download,
  Feather,
  Fullscreen,
  MessageCircle,
  Minus,
  Plus,
  Pointer,
  RefreshCw,
} from "@lucide/vue";
import {
  useElementBounding,
  useFullscreen,
  useResizeObserver,
  useWindowSize,
} from "@vueuse/core";
import { useRouteQuery } from "@vueuse/router";
import { toBlob } from "html-to-image";
import { clamp } from "lodash";

/** element refs */
const rightPanelElement = useTemplateRef("rightPanelElement");
const mapGridElement = useTemplateRef("mapGridElement");
const mapElement = useTemplateRef("mapElement");

/** default selected maps */
const defaultSelected = [
  {
    level: "county",
    statistic: "sociodemographics;Total",
    locations: [],
  },
];

type SelectedMap = {
  level: string;
  statistic: string;
  locations: string[];
};

/** selected state */
const selectedMaps = useDeepRouteQuery<SelectedMap[]>("map", defaultSelected);
/** selected map index */
const selectedIndex = ref(0);
/** get selected map object */
const selectedMap = () => {
  const selected = selectedMaps.value[selectedIndex.value];
  if (!selected) throw Error("Selected map index out of bounds");
  return selected;
};

/** map zoom state */
const zoom = useRouteQuery("zoom", "0", { transform: numberParam });
const lat = useRouteQuery("lat", "0", { transform: numberParam });
const long = useRouteQuery("long", "0", { transform: numberParam });

/** map style state */
const showLegends = ref(true);
const selectedBackground = ref(defaultBackground);
const selectedGradient = ref(defaultGradient);
const backgroundOpacity = ref(1);
const geographyOpacity = ref(0.75);
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

/** load geographic level data */
const {
  query: loadLevels,
  data: levels,
  status: levelStatus,
} = useQuery(getLevels, {});
onMounted(loadLevels);

/** geographic levels, as select options */
const levelOptions = computed(() =>
  Object.entries(levels.value).map(([level, { label }]) => ({
    id: level,
    label,
  })),
);

/** load statistic data */
const {
  query: loadStatistics,
  data: statistics,
  status: statisticStatus,
} = useQuery(getStatistics, {});
onMounted(loadStatistics);

type Groups = {
  [group: string]: Groups | null;
};

/** statistics, as tree options */
const statisticOptions = computed(() => {
  const getTree = (group: Groups = statisticGroups): Tree[] =>
    Object.entries(group).map(([statistic, value]) => ({
      id: statistic,
      label: statistics.value?.[statistic]?.label ?? statistic,
      children: value ? getTree(value) : [],
    }));
  return getTree();
});

/** load location data */
const {
  query: loadLocations,
  data: locations,
  status: locationsStatus,
} = useQuery(getLocations, {});
onMounted(loadLocations);

/** locations, as select options */
const locationOptions = computed(() =>
  Object.entries(locationGroups).flatMap(([group, list]) => [
    { group },
    ...Object.keys(list).map((location) => ({
      id: location,
      label: locations.value[location]?.label ?? "",
    })),
  ]),
);

/** load maps data */
const {
  query: loadMapData,
  data: mapData,
  status: mapDataStatus,
} = useQuery(() => {
  /** query all maps in parallel */
  return Promise.all(
    selectedMaps.value.map(async (selected) => {
      /** load geography */
      const geography = await getLevel(selected.level);
      /** load statistic */
      const statistic = await getStatistic(
        selected.statistic,
        selected.level,
        {},
      );
      /** load locations */
      const locations = await Promise.all(selected.locations.map(getLocation));

      /** add extra properties to geography */
      const geographyExtras = {
        ...geography,
        features: geography.features.map((feature) => {
          const value = getValue(statistic.values, feature.id);
          return {
            ...feature,
            properties: {
              ...feature.properties,
              id: feature.id,
              selected,
              value: value?.value,
              aac: value?.aac,
            },
          };
        }),
      };

      return { selected, geography: geographyExtras, statistic, locations };
    }),
  );
}, []);

/** re-load data when selected maps change */
watch(selectedMaps, loadMapData, { immediate: true, deep: true });

/** page title */
watchEffect(() => {
  const maps = selectedMaps.value.length;
  const statistic = statistics.value[selectedMap().statistic]?.label;
  const locations = selectedMap().locations.length;
  appTitle.value = [
    maps > 1 ? `${maps.toLocaleString()} maps` : "",
    statistic ? statistic : "",
    locations ? `${locations.toLocaleString()} locations` : "",
  ].filter(Boolean);
});

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
    case 9:
    case 11:
      return 3;
    case 8:
    case 12:
      return 4;
    case 10:
      return 5;
  }
  return 3;
});

/** download statistic from tree click */
const onTreeDownload = (statistic = "") =>
  getDownload(selectedMap().level, statistic);

/** reset customizations and map to defaults */
const reset = async () => {
  zoom.value = 0;
  lat.value = 0;
  long.value = 0;
  showLegends.value = true;
  selectedBackground.value = defaultBackground;
  selectedGradient.value = defaultGradient;
  backgroundOpacity.value = 1;
  geographyOpacity.value = 0.75;
  locationOpacity.value = 1;
  flipGradient.value = false;
  scaleSteps.value = 6;
  niceSteps.value = false;
  scalePower.value = 1;
  manualMinMax.value = false;
  mapWidth.value = 0;
  mapHeight.value = 0;
};

/** fit all maps */
const fit = () => mapElement.value?.forEach((map) => map?.fit());

/** auto-adjust right panel/map height */
const autoRightPanelHeight = ref(0);
const { top: rightPanelTop, update: updateRightPanelHeight } =
  useElementBounding(rightPanelElement);
useResizeObserver(document.body, updateRightPanelHeight);
const { height: windowHeight } = useWindowSize();
watchEffect(() => {
  if (windowHeight.value < 400) return;
  if (!rightPanelTop.value) return;
  if (mapWidth.value || mapHeight.value) return;
  const max = windowHeight.value - 20;
  const height = clamp(max - rightPanelTop.value, 400, max);
  if (Math.abs(height - autoRightPanelHeight.value) > 1)
    autoRightPanelHeight.value = height;
});

/** download maps as pngs */
const downloadMapImage = async () => {
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

/** download maps as geo data */
const downloadMapGeo = async () => {
  if (!mapElement.value?.length) return;

  /** download json files */
  for (const map of mapElement.value) {
    const geo = map?.getGeo();
    if (!geo) continue;
    downloadJson(geo, "map-geo");
  }
};

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(mapGridElement);
</script>
