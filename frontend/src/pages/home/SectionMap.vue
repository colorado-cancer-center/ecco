<template>
  <div
    class="grid grid-cols-[--spacing(100)_1fr] gap-8 max-md:grid-cols-1"
    :style="{ '--cols': mapCols }"
  >
    <!-- left panel -->
    <div class="flex flex-col gap-8 text-left" role="group">
      <!-- level selection -->
      <AppSelect
        v-model="selectedLevel"
        label="Geographic level"
        :options="levelOptions"
      />

      <!-- category/measure selection -->
      <div class="flex flex-col gap-1">
        Statistics
        <AppTree
          :children="measureMap"
          :model-value="treeValue"
          @update:model-value="onTreeChange"
        >
          <template #default="{ parents }">
            <button
              v-if="parents.at(-1)?.id"
              v-tooltip="'Download measure data'"
              class="size-8 rounded-md text-stone-300 hover:text-black"
              @click="onTreeDownload(parents.at(-1)?.id)"
            >
              <Download />
            </button>
          </template>
        </AppTree>
      </div>

      <!-- factors -->
      <template v-if="!isEmpty(factors)">
        <div class="grid grid-cols-[min-content_1fr] items-center gap-2">
          <template v-for="(factor, index) in factors" :key="index">
            <AppSelect
              v-if="selectedFactors[index]"
              class="contents!"
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
        label="Resources & Other Locations"
        :options="locationOptions"
        :multi="true"
        tooltip="Resources and other locations to show on map, e.g. screening centers, clinics, specialists"
      />

      <!-- multi-map compare -->
      <AppCollapsible label="Compare">
        <div class="grid grid-cols-3 gap-2">
          <AppButton
            v-if="inCompare()"
            v-tooltip="'Remove selected map from comparison'"
            v-bind="highlightListeners(findInCompare())"
            @click="toggleCompare()"
          >
            <Minus />
            Remove
          </AppButton>
          <AppButton
            v-else
            v-tooltip="'Add selected map to comparison'"
            v-bind="highlightListeners(thumbnails.length - 1)"
            :disabled="compare.length >= maxCompare"
            @click="toggleCompare()"
          >
            <Plus />
            Add
          </AppButton>
          <AppButton
            v-if="compare.length"
            v-tooltip="'Remove all maps from comparison and reset'"
            @click="compare = []"
          >
            <X />
            Clear
          </AppButton>
          <AppButton
            v-if="showPreview && compare.length && !inCompare()"
            v-tooltip="'Hide preview of selected map'"
            v-bind="highlightListeners(thumbnails.length - 1)"
            @click="showPreview = false"
          >
            Hide Preview
          </AppButton>
        </div>

        <template v-if="compare.length">
          <div class="flex flex-wrap items-center justify-center gap-2">
            Comparing {{ compare.length }} map(s):
          </div>

          <div class="grid grid-cols-3 place-items-center gap-2">
            <template v-for="(map, index) in compare" :key="index">
              <AppButton
                v-if="index < compare.length"
                v-tooltip="'Remove map from comparison'"
                v-bind="highlightListeners(index)"
                class="group relative aspect-2/1 w-full"
                @click="toggleCompare(map)"
              >
                <Minus />
                <img
                  v-if="thumbnails[index]"
                  :src="thumbnails[index]"
                  alt=""
                  class="absolute size-full object-contain object-center group-hover:opacity-0"
                />
              </AppButton>
            </template>

            <div
              v-for="(_, index) in Array(
                Math.min(round(compare.length + 1, 3, 'ceil'), maxCompare) -
                  compare.length,
              )"
              :key="index"
              v-tooltip="
                'Select new measure/locations/etc. to compare another map'
              "
              class="aspect-2/1 w-full rounded-md border border-stone-300"
            />
          </div>
        </template>
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
          v-model="geometryOpacity"
          v-tooltip="'Transparency of geometry layer'"
          label="Geometry transparency"
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
        v-if="renderMap"
        ref="mapGridElement"
        class="grid h-(--height) w-(--width) grid-cols-[repeat(var(--cols),1fr)] gap-1 bg-stone-600 shadow-md transition max-md:h-[90dvh]"
        :class="[
          mapDataStatus === 'loading' && 'preview',
          mapHeight ? 'shrink-0' : 'grow',
        ]"
        :style="{
          '--width': mapWidth ? `${mapWidth}px` : '',
          '--height': mapHeight ? `${mapHeight}px` : '',
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
          :class="[
            showPreview && compare.length && !inCompare(selected) && 'preview',
            index === highlightedThumbnail
              ? 'z-10 outline-8 outline-theme'
              : 'outline-8 outline-transparent',
          ]"
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
              {{ getLabel(selected.category, selected.measure).at(-1) }}
            </strong>
            <div class="text-sm">{{ upperFirst(selected.level) }}</div>
            <div>
              {{
                Object.values(selected.factors)
                  .filter((factor) => !factor.match(/(^|\s)all($|\s)/i))
                  .join(", ")
              }}
            </div>
          </template>

          <template #top-left-lower>
            <div v-if="values?.source" class="flex items-center gap-2">
              <AppLink :to="values.source.link ?? ''">
                {{ values.source.name ?? "source" }}
              </AppLink>
              <AppButton
                v-tooltip="'Copy citation text to clipboard'"
                class="min-h-0! min-w-0! p-1!"
                data-save-hide
                @click="copy(getSourceCitation(values.source))"
              >
                <Copy />
              </AppButton>
            </div>

            <div v-if="values?.state">
              State-wide: {{ formatValue(values.state, values.unit) }}
            </div>
          </template>

          <template v-if="countyWide.length" #top-right>
            <b>Outreach</b>
            <div class="grid grid-cols-[auto_auto] items-center gap-4">
              <template
                v-for="(field, countyIndex) of countyWide"
                :key="countyIndex"
              >
                <div
                  class="flex size-4 items-center justify-center border border-black text-white"
                  :style="{ backgroundColor: field.color }"
                >
                  <Check />
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
            <div class="grid grid-cols-[auto_auto] items-center gap-4">
              <template
                v-for="(field, countyIndex) of countyWide"
                :key="countyIndex"
              >
                <div v-if="field.checkKey && feature[field.checkKey]">
                  <span
                    v-if="field.countKey && feature[field.countKey]"
                    class="flex size-4 items-center justify-center border border-black text-white"
                    :style="{ backgroundColor: field.color }"
                  >
                    {{ feature[field.countKey] }}
                  </span>
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

            <p>
              <AppLink
                v-if="selectedLevel === 'tract' || noData"
                to="/sources#suppressed-values"
                :new-tab="true"
                class="inline-flex items-center gap-1 underline"
              >
                Low values may be suppressed
                <Info />
              </AppLink>
            </p>

            <i>
              {{ getLabel(selected.category, selected.measure).join(" > ") }}
            </i>

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
                  {{ formatValue(feature.value, values?.unit) }}
                </dd>
              </template>

              <template
                v-if="
                  typeof feature.aac === 'number' ||
                  typeof feature.aac === 'string'
                "
              >
                <dt>Avg. Annual Count</dt>
                <dd>{{ formatValue(feature.aac, values?.unit) }}</dd>
              </template>

              <template v-if="feature.count">
                <dt>Count</dt>
                <dd>{{ formatValue(feature.count) }}</dd>
              </template>

              <!-- extra info -->

              <template v-if="feature.counties">
                <dt>Counties</dt>
                <dd>
                  <template
                    v-for="(county, countyIndex) in feature.counties.split(
                      ', ',
                    )"
                    :key="countyIndex"
                  >
                    {{ county }}<br />
                  </template>
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

              <template v-if="outreachSelected.length">
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
              </template>
            </dl>

            <!-- actions -->

            <AppButton
              v-if="selected.level === 'county' && 'county' in feature"
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
import type { ShallowRef } from "vue";
import type {
  Facets,
  GeoProps,
  LocationList,
  LocationProps,
  Values,
} from "@/api";
import type { Entry, Option } from "@/components/AppSelect.vue";
import type { Expand, Update } from "@/util/types";
import {
  computed,
  onMounted,
  ref,
  shallowRef,
  unref,
  useTemplateRef,
  watch,
  watchEffect,
} from "vue";
import { event } from "vue-gtag";
import {
  extraLocationList,
  getDownload,
  getGeo,
  getLocation,
  getSourceCitation,
  getValues,
  outreachLocationKey,
} from "@/api";
import measureMap from "@/api/measure-map.json";
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
import { colors } from "@/components/markers";
import { appTitle } from "@/meta";
import { numberParam } from "@/pages";
import { useQuery } from "@/util/composables";
import { downloadJson, downloadPng } from "@/util/download";
import { formatValue, round } from "@/util/math";
import { copy, sleep } from "@/util/misc";
import {
  Check,
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
import { useRouteQuery } from "@vueuse/router";
import { toBlob } from "html-to-image";
import {
  clamp,
  isEmpty,
  isEqual,
  mapValues,
  orderBy,
  pick,
  uniqWith,
  upperFirst,
} from "lodash";

type Value = NonNullable<Values>["values"][string];

type FeatureInfo = Expand<
  Partial<
    GeoProps &
      LocationProps &
      /** "value" can also be string because of explicit scale */
      Update<Value, "value", string>
  >
>;

type Props = {
  /** level/category/measure */
  facets: Facets;
  locationList: LocationList;
};

const { facets, locationList } = defineProps<Props>();

/** element refs */
const rightPanelElement = useTemplateRef("rightPanelElement");
const mapGridElement = useTemplateRef("mapGridElement");
const mapElement = useTemplateRef("mapElement");

/** select boxes state */
const selectedLevel = useRouteQuery<string>("level", "");
const selectedCategory = useRouteQuery<string>("category", "");
const selectedMeasure = useRouteQuery<string>("measure", "");
const selectedFactors = shallowRef<Record<string, ShallowRef<string>>>({});
const selectedLocations = ref<string[]>([]);

/** map zoom state */
const zoom = useRouteQuery("zoom", "0", { transform: numberParam });
const lat = useRouteQuery("lat", "0", { transform: numberParam });
const long = useRouteQuery("long", "0", { transform: numberParam });

/** map style state */
const showLegends = ref(true);
const selectedBackground = ref(defaultBackground);
const selectedGradient = ref(defaultGradient);
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

/** compare state */
const compare = ref<Map[]>([]);
const showPreview = ref(true);

/** page title */
watchEffect(() => {
  const locations = selectedLocations.value.length;
  appTitle.value = [
    selectedMeasure.value,
    locations ? `${locations} locations` : "",
  ].filter(Boolean);
});

/** push selected facet values to tree value */
const treeValue = computed(() => [
  `${selectedCategory.value};${selectedMeasure.value}`,
]);

/** pull tree value from selected facet values */
const onTreeChange = (value: string[]) => {
  [selectedCategory.value = "", selectedMeasure.value = ""] =
    value.at(-1)?.split(";") ?? [];
};

/** download measure from tree click */
const onTreeDownload = (value = "") => {
  if (!value) return;
  const [category = "", measure = ""] = value.split(";");
  if (!category || !measure) return;
  getDownload(selectedLevel.value, category, measure);
  event("downloadMeasure", {
    _value: { level: selectedLevel.value, category, measure },
  });
};

/** geographic level options */
const levelOptions = computed<Option[]>(() =>
  Object.entries(facets)
    .filter(
      ([, { categories }]) =>
        categories[selectedCategory.value]?.measures[selectedMeasure.value],
    )
    .map(([level, { label }]) => ({ id: level, label })),
);

/** get label parts from selected */
const getLabel = (category = "", measure = "") => {
  type Leaf = { id?: string; label?: string; children?: Leaf[] };
  const selected = `${category};${measure}`;
  const getPath = (children: Leaf[], path: Leaf[] = []): Leaf[] =>
    children.flatMap(({ children = [], ...leaf }) =>
      leaf.id === selected
        ? [...path, leaf]
        : getPath(children, [...path, leaf]),
    );
  return getPath(measureMap)
    .map((part) => part.label || "")
    .filter(Boolean);
};

/** auto-select facets */
onMounted(() => {
  if (
    !selectedLevel.value &&
    !selectedCategory.value &&
    !selectedMeasure.value
  ) {
    selectedLevel.value = "county";
    selectedCategory.value = "sociodemographics";
    selectedMeasure.value = "Total";
  }
});

/** auto-select level */
watchEffect(() => {
  if (!levelOptions.value.find((option) => option.id === selectedLevel.value))
    selectedLevel.value = levelOptions.value[0]?.id || "";
});

/** stratification factors (e.g. race/ethnicity, sex, etc) */
const factors = computed(
  () =>
    facets[selectedLevel.value]?.categories[selectedCategory.value]?.measures[
      selectedMeasure.value
    ]?.factors || {},
);

/** full selected map */
const selectedMap = computed(() => ({
  level: selectedLevel.value,
  category: selectedCategory.value,
  measure: selectedMeasure.value,
  /** unwrap nested refs */
  factors: mapValues(selectedFactors.value, (factor) => factor.value),
  locations: selectedLocations.value,
}));

type Map = typeof selectedMap.value;

/** reenable preview state on any change to comparison */
watch(compare, () => (showPreview.value = true), { deep: true });

/** map thumbnail blob urls */
const thumbnails = ref<string[]>([]);

/** highlighted thumbnail */
const highlightedThumbnail = ref<number | null>(null);

/** event listeners to handle map highlighting */
const highlightListeners = (index: number) => ({
  onfocus: () => (highlightedThumbnail.value = index),
  onblur: () => (highlightedThumbnail.value = null),
  onmouseenter: () => (highlightedThumbnail.value = index),
  onmouseleave: () => (highlightedThumbnail.value = null),
});

/** are two map selections equal */
const mapsEqual = (a: Map, b: Map) =>
  a.level === b.level &&
  a.category === b.category &&
  a.measure === b.measure &&
  Object.entries(a.factors).every(
    ([key, value]) => unref(b.factors[key]) === unref(value),
  ) &&
  isEqual(a.locations, b.locations);

/** find (selected) map in compare group */
const findInCompare = (map?: Map) => {
  map ??= selectedMap.value;
  return compare.value.findIndex((entry) => mapsEqual(map, entry));
};

/** is (selected) map already in compare group */
const inCompare = (map?: Map) => findInCompare(map) !== -1;

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

/** analytics, capture individual state changes */
watchEffect(() => event("selectLevel", { _value: selectedLevel.value }));
watchEffect(() => event("selectCategory", { _value: selectedCategory.value }));
watchEffect(() => event("selectMeasure", { _value: selectedMeasure.value }));
watchEffect(() =>
  event("selectFactors", {
    _value: mapValues(selectedFactors.value, (factor) => factor.value),
  }),
);
watchEffect(() =>
  event("selectLocations", { _value: selectedLocations.value }),
);
/** (watchEffect's auto-dependency-detection doesn't work here for some reason) */
watch(compare, () => event("compare", { _value: compare.value }), {
  deep: true,
  immediate: true,
});

/** load maps data */
const {
  query: loadMapData,
  data: mapData,
  status: mapDataStatus,
} = useQuery(
  () => {
    /** analytics, capture full user selection state in same object */
    event("loadMapData", { _value: selectedMaps.value });

    /** query all maps in parallel */
    return Promise.all(
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
    );
  },
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
  selectedBackground.value = defaultBackground;
  selectedGradient.value = defaultGradient;
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

/** map of location id to human-readable label */
const locationLabels = computed(() =>
  Object.fromEntries(
    Object.values(locationList)
      .map((value) => Object.entries(value))
      .flat()
      .map(([label, id]) => [id, label] as const),
  ),
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
      Object.values(extraLocationList[outreachLocationKey]) as string[]
    ).includes(location),
  ),
);

/** county overview outreach data */
const countyWide = computed(() => {
  /** get selected overview fields */
  let selected = Object.entries(
    pick(extraLocationList[outreachLocationKey], [
      "Tobacco Cessation App Users",
    ]),
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
