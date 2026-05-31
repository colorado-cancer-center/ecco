<script setup lang="ts">
import type { Tree } from "@/components/AppTree.vue";
import type { ValueOf } from "type-fest";
import {
  computed,
  onMounted,
  ref,
  toRaw,
  useTemplateRef,
  watch,
  watchEffect,
} from "vue";
import {
  extraLocations,
  getDownloadStatistic,
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
import { jsonParam, numberParam, useParam } from "@/pages";
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
  Info,
  MessageCircle,
  Minus,
  Plus,
  Pointer,
  RefreshCw,
  X,
} from "@lucide/vue";
import {
  useElementBounding,
  useFullscreen,
  useResizeObserver,
  useWindowSize,
} from "@vueuse/core";
import { toBlob } from "html-to-image";
import { clamp } from "lodash";

/** element refs */
const rightPanelElement = useTemplateRef("rightPanelElement");
const mapGridElement = useTemplateRef("mapGridElement");
const mapElements = useTemplateRef("mapElements");

/** default selected maps */
const defaultMap = () => ({
  level: "county",
  statistic: "sociodemographics;Total",
  factors: {},
  locations: [],
});

type SelectedMap = {
  level: string;
  statistic: string;
  factors: Record<string, string>;
  locations: string[];
};

/** selected maps state */
const selectedMaps = useParam(
  "maps",
  [defaultMap()],
  jsonParam<SelectedMap[]>([]),
);

/** maximum maps to be compared */
const maxMaps = 12;

/** selected map index */
const selectedIndex = ref(0);

/** get selected map object */
const selectedMap = () => {
  const selected = selectedMaps.value[selectedIndex.value];
  if (!selected) throw Error("selected map out of bounds");
  return selected;
};

/** map zoom state */
const zoom = useParam("zoom", 0, numberParam);
const lat = useParam("lat", 0, numberParam);
const long = useParam("long", 0, numberParam);

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

onMounted(async () => {
  await loadLevels();
  console.debug("levels", toRaw(levels.value));
});

/** geographic levels, as select options */
const levelOptions = computed(() =>
  Object.entries(levels.value).map(([level, { label }]) => ({
    id: level,
    label:
      label +
      (statistics.value[selectedMap().statistic]?.levels.includes(level)
        ? ""
        : " (ND)"),
  })),
);

/** load statistic data */
const {
  query: loadStatistics,
  data: statistics,
  status: statisticStatus,
} = useQuery(getStatistics, {});

onMounted(async () => {
  await loadStatistics();
  console.debug("statistics", toRaw(statistics.value));
});

export type Groups = {
  [group: string]: Groups | null;
};

/** statistics, as tree options */
const statisticOptions = computed(() => {
  const getTree = (groups: Groups = statisticGroups): Tree[] =>
    Object.entries(groups).map(([statisticOrGroup, value]) => ({
      id: statisticOrGroup,
      label: statistics.value[statisticOrGroup]?.label ?? statisticOrGroup,
      children: value ? getTree(value) : [],
    }));
  return getTree();
});

/** statistics, as grouping paths */
const statisticPaths = computed(() => {
  const flatten = (groups: Groups, path: string[] = []): string[][] =>
    Object.entries(groups).flatMap(([key, value]) =>
      value === null ? [[...path, key]] : flatten(value, [...path, key]),
    );
  const paths = flatten(statisticGroups);
  return Object.fromEntries(
    paths.map((path) => {
      const id = path.at(-1) ?? "";
      const parents = path.slice(0, -1);
      const statistic = statistics.value[id]?.label ?? id;
      return [id, parents.concat(statistic)];
    }),
  );
});

/** load location data */
const {
  query: loadLocations,
  data: locations,
  status: locationsStatus,
} = useQuery(getLocations, {});

onMounted(async () => {
  await loadLocations();
  console.debug("locations", toRaw(locations.value));
});

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
} = useQuery(async () => {
  /** query all maps in parallel */
  const maps = await Promise.all(
    toRaw(selectedMaps.value).map(async (selected) => {
      /** load geography */
      const geography = await getLevel(selected.level);
      /** load statistic */
      const statistic = await getStatistic(
        selected.statistic,
        selected.level,
        selected.factors,
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
              statistic:
                statistics.value[selected.statistic]?.label ??
                selected.statistic,
              value: value?.value,
              aac: value?.aac,
            },
          };
        }),
      };

      return { selected, geography: geographyExtras, statistic, locations };
    }),
  );

  console.debug("maps", maps);

  return maps;
}, []);

/** re-load data when selected maps change */
watch(selectedMaps, loadMapData, { immediate: true, deep: true });

/** all possible factors for any statistic */
const factors = computed(() => {
  const factors: ValueOf<typeof statistics.value>["factors"] = {};
  for (const statistic of Object.values(statistics.value))
    for (const [factor, { label, values }] of Object.entries(
      statistic.factors,
    )) {
      factors[factor] ??= { label, values: {} };
      for (const [value, { label }] of Object.entries(values))
        if (!(value in factors[factor].values))
          factors[factor].values[value] = { label };
    }

  console.debug("factors", toRaw(factors));

  return factors;
});

/** auto-select default factors */
watchEffect(() => {
  /** factors available for selected statistic */
  const available = Object.keys(
    statistics.value[selectedMap().statistic]?.factors ?? {},
  );

  for (const factor of available) {
    /** if already selected, ignore */
    if (factor in selectedMap().factors) continue;
    /** first value is default */
    const _default = Object.keys(factors.value[factor]?.values ?? {}).at(0);
    if (!_default) continue;
    /** set default */
    selectedMap().factors[factor] = _default;
  }
});

/** page title */
watchEffect(() => {
  const maps = selectedMaps.value.length;
  const statistic = statistics.value[selectedMap().statistic]?.label;
  const locations = selectedMap().locations.length;
  appTitle.value = [
    maps > 1 ? `${maps.toLocaleString()} maps` : statistic ? statistic : "",
    locations ? `${locations.toLocaleString()} locations` : "",
  ].filter(Boolean);
});

/** add map to comparison */
const addMap = () => {
  selectedMaps.value.push(defaultMap());
  selectedIndex.value = selectedMaps.value.length - 1;
};

/** delete map from comparison */
const deleteMap = (index: number) => {
  /** index in range */
  if (index < 0 || index >= selectedMaps.value.length) return;

  /** delete map */
  selectedMaps.value.splice(index, 1);

  if (selectedMaps.value.length === 0) {
    /** no maps left */
    addMap();
    selectedIndex.value = 0;
  } else if (index < selectedIndex.value) {
    /** deleted index is before selected index */
    selectedIndex.value--;
  } else if (
    index === selectedMaps.value.length &&
    selectedIndex.value === selectedMaps.value.length
  ) {
    /** deleted and selected index are at end */
    selectedIndex.value--;
  }
};

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
  getDownloadStatistic(selectedMap().level, statistic);

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
const fit = () => mapElements.value?.forEach((map) => map?.fit());

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
  if (!mapElements.value?.length) return;

  /** download json files */
  for (const map of mapElements.value) {
    const geo = map?.getGeo();
    if (!geo) continue;
    downloadJson(geo, "map-geo");
  }
};

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(mapGridElement);
</script>

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
        :class="[levelStatus === 'loading' && 'animate-loading']"
      />

      <!-- statistics -->
      <AppTree
        v-model="selectedMap().statistic"
        :tree="statisticOptions"
        :class="[statisticStatus === 'loading' && 'animate-loading']"
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

      <!-- factors -->
      <div
        class="grid grid-cols-[min-content_1fr] items-center gap-2 empty:hidden"
      >
        <template
          v-for="({ label, values }, factor, index) in factors"
          :key="index"
        >
          <AppSelect
            v-if="
              /** if factor available for statistic */
              factor in (statistics[selectedMap().statistic]?.factors ?? {})
            "
            v-model="selectedMap().factors[factor]!"
            :options="
              Object.entries(values).map(([id, { label }]) => ({ id, label }))
            "
            class="contents!"
            :label="label"
          />
        </template>
      </div>

      <!-- locations -->
      <AppSelect
        v-model="selectedMap().locations"
        multi
        :options="locationOptions"
        label="Resources & Other Locations"
        :class="[locationsStatus === 'loading' && 'animate-loading']"
      />

      <!-- multi-map compare -->
      <AppCollapsible label="Compare">
        <div class="grid grid-cols-3 gap-4">
          <div
            v-for="(selected, index) in selectedMaps"
            :key="index"
            class="relative aspect-4/3"
          >
            <button
              class="size-full overflow-hidden border-2 bg-stone-100"
              :class="
                selectedIndex === index
                  ? 'border-theme'
                  : 'border-stone-100 hover:border-theme'
              "
              @click="selectedIndex = index"
            >
              <img
                v-if="mapElements?.[index]?.thumbnail"
                :src="mapElements?.[index]?.thumbnail"
                alt=""
                class="size-full object-contain"
              />
            </button>

            <button
              class="absolute top-0.5 right-0.5 z-10 size-6 bg-stone-100 hover:text-theme"
              @click="deleteMap(index)"
            >
              <X />
            </button>
          </div>
        </div>
        <AppButton :disabled="selectedMaps.length >= maxMaps" @click="addMap()">
          Add
          <Plus />
        </AppButton>
      </AppCollapsible>

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
          mapDataStatus === 'loading' && 'animate-loading',
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
          ref="mapElements"
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
          <template #top-left-upper>
            <div class="flex flex-col gap-1">
              <div
                v-for="(part, index) in [
                  levels[selected.level]?.label,
                  ...(statisticPaths[selected.statistic] ?? []),
                ]"
                :key="index"
                class="not-last:text-sm last:font-bold"
              >
                {{ part }}
              </div>
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
            <div v-if="statistic.source" class="flex items-center gap-2">
              <AppLink :to="statistic.source.link" class="text-sm">
                {{ statistic.source.label }}
                <template v-if="statistic.source.id">
                  ({{ statistic.source.id }})
                </template>
                {{ statistic.source.date }}
              </AppLink>
              <AppButton
                v-if="getSourceCitation(statistic.source)"
                v-tooltip="'Copy citation text to clipboard'"
                class="size-8 min-h-0! min-w-0! shrink-0 p-0!"
                data-save-hide
                @click="copy(getSourceCitation(statistic.source))"
              >
                <Copy />
              </AppButton>
            </div>

            <div v-if="statistic.state">
              State: {{ formatValue(statistic.state, statistic.unit) }}
            </div>
          </template>

          <!-- feature popup -->
          <template #popup="{ feature }">
            {{ console.debug("feature", feature) }}

            <dl>
              <!-- overview -->

              <template v-if="feature.name">
                <dt>Name</dt>
                <dd>{{ feature.name }}</dd>
              </template>

              <template v-if="feature.level">
                <dt>Level</dt>
                <dd>{{ feature.level }}</dd>
              </template>

              <template v-if="feature.county">
                <dt>County</dt>
                <dd>{{ feature.county }}</dd>
              </template>

              <template v-if="feature.zip">
                <dt>Zip</dt>
                <dd>{{ feature.zip }}</dd>
              </template>

              <!-- values -->

              <template v-if="feature.statistic">
                <dt>Statistic</dt>
                <dd>{{ feature.statistic }}</dd>
              </template>

              <template v-if="feature.location">
                <dt>Info</dt>
                <dd>{{ feature.location }}</dd>
              </template>

              <template v-if="feature.value !== undefined">
                <dt>{{ feature.aac ? "Rate" : "Value" }}</dt>
                <dd>{{ formatValue(feature.value, statistic.unit) }}</dd>
              </template>

              <template v-if="feature.aac !== undefined">
                <dt>Avg. Annual Count</dt>
                <dd>{{ formatValue(feature.aac, statistic.unit) }}</dd>
              </template>

              <div v-if="feature.value === undefined" class="col-span-full">
                <AppLink
                  to="/sources#suppressed-values"
                  :new-tab="true"
                  class="inline-flex items-center gap-1 underline"
                >
                  Low values may be suppressed
                  <Info />
                </AppLink>
              </div>

              <!-- extra info -->

              <template v-if="feature.description">
                <dt>Description</dt>
                <dd>{{ feature.description }}</dd>
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

              <template
                v-if="
                  selected.locations.some(
                    (location) => location in extraLocations,
                  )
                "
              >
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
                      Tobacco Cessation App Users
                    </AppLink>
                  </dt>
                  <dd>{{ formatValue(feature["2morrow_signups"]) }}</dd>
                </template>
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
            @click="mapElements?.forEach((map) => map?.zoomOut())"
          >
            <Minus />
          </AppButton>
          <AppButton
            v-tooltip="'Zoom in'"
            @click="mapElements?.forEach((map) => map?.zoomIn())"
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
