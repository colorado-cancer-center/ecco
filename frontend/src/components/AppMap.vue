<template>
  <div class="container">
    <div ref="scroll" class="scroll">
      <!-- map container -->
      <div
        ref="element"
        class="map"
        :style="{
          width: width ? width + 'px' : '100%',
          height: height ? height + 'px' : '100%',
        }"
      />
    </div>

    <!-- control set -->
    <div class="controls">
      <AppButton
        v-tooltip="'Download current map view as PNG'"
        :icon="faDownload"
        :accent="true"
        @click="download"
      >
        Download Map
      </AppButton>
      <AppButton
        v-tooltip="'Zoom out'"
        :icon="faMinus"
        @click="map?.zoomOut()"
      />
      <AppButton v-tooltip="'Zoom in'" :icon="faPlus" @click="map?.zoomIn()" />
      <AppButton
        v-tooltip="'Fit view to data'"
        :icon="faCropSimple"
        @click="fit"
      >
        Fit
      </AppButton>
      <AppButton
        v-tooltip="'View map in full screen'"
        :icon="faExpand"
        @click="fullscreen"
      >
        Fullscreen
      </AppButton>
    </div>

    <!-- top left legend -->
    <Teleport v-if="showLegends && topLeftLegend" :to="topLeftLegend">
      <div v-stop class="legend">
        <slot name="top-left" />

        <!-- scale key -->
        <div class="steps">
          <template
            v-for="(step, index) of [...scale.steps].reverse()"
            :key="index"
          >
            <svg viewBox="0 0 1 1">
              <rect x="0" y="0" width="1" height="1" :fill="step.color" />
            </svg>
            <span>{{ formatValue(step.lower, percent) }}</span>
            <span>&ndash;</span>
            <span>{{ formatValue(step.upper, percent) }}</span>
          </template>
          <template v-if="noData">
            <svg viewBox="0 0 1 1">
              <rect x="0" y="0" width="1" height="1" :fill="noDataColor" />
            </svg>
            <span style="grid-column: 2 / -1">No data</span>
          </template>
        </div>
      </div>
    </Teleport>

    <!-- top right legend -->
    <Teleport v-if="showLegends && topRightLegend" :to="topRightLegend">
      <div v-stop class="legend">
        <slot name="top-right" />
      </div>
    </Teleport>

    <!-- bottom right legend -->
    <Teleport v-if="showLegends && bottomRightLegend" :to="bottomRightLegend">
      <div v-stop class="legend">
        <slot name="bottom-right" />

        <!-- symbol key -->
        <div v-if="Object.keys(symbols).length" class="symbols">
          <template v-for="(symbol, index) of symbols" :key="index">
            <img :src="symbol.image" alt="" />
            <small>{{ symbol.label }}</small>
          </template>
        </div>
      </div>
    </Teleport>

    <!-- county/tract popup -->
    <Teleport v-if="popup && popupFeature" :to="popup">
      <!-- name -->
      <template v-if="popupFeature.name">
        <strong>{{ popupFeature.name }}</strong>
      </template>

      <div class="mini-table">
        <!-- primary "value" for feature -->
        <template v-if="values[popupFeature.id]">
          <span>{{
            typeof values[popupFeature.id]?.aac === "number" ? "Rate" : "Value"
          }}</span>
          <span>{{
            formatValue(values[popupFeature.id]?.value || 0, percent, false)
          }}</span>
        </template>

        <!-- age adjusted count -->
        <template v-if="typeof values[popupFeature.id]?.aac === 'number'">
          <span>Avg. Annual Count</span>
          <span>{{
            formatValue(values[popupFeature.id]?.aac || 0, false, false)
          }}</span>
        </template>

        <!-- organization -->
        <template v-if="popupFeature.org">
          <span>Org</span>
          <span>{{ popupFeature.org }}</span>
        </template>

        <!-- link -->
        <template v-if="popupFeature.link">
          <span>Link</span>
          <AppLink :to="popupFeature.link" class="truncate">
            {{ popupFeature.link.replace(/(https?:\/\/)?(www\.)?/, "") }}
          </AppLink>
        </template>

        <!-- address -->
        <template v-if="popupFeature.address">
          <span>Address</span>
          <span>{{ popupFeature.address }}</span>
        </template>

        <!-- phone -->
        <template v-if="popupFeature.phone">
          <span>Phone</span>
          <span>{{ popupFeature.phone }}</span>
        </template>

        <!-- notes -->
        <template v-if="popupFeature.notes">
          <span>Notes</span>
          <span>{{ popupFeature.notes }}</span>
        </template>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import * as d3 from "d3";
import domtoimage from "dom-to-image";
import type { GeoJsonProperties } from "geojson";
import L, { type MapOptions } from "leaflet";
import { debounce, mapValues } from "lodash";
import {
  faCropSimple,
  faDownload,
  faExpand,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons";
import { useElementSize, useFullscreen, useResizeObserver } from "@vueuse/core";
import type { Data, Locations, Values } from "@/api";
import AppButton from "@/components/AppButton.vue";
import { getGradient } from "@/components/gradient";
import { markerOptions } from "@/components/markers";
import { useScrollable } from "@/util/composables";
import { downloadPng } from "@/util/download";
import { formatValue, isPercent, normalizedApply } from "@/util/math";
import { getBbox, sleep } from "@/util/misc";
import "leaflet/dist/leaflet.css";
import AppLink from "@/components/AppLink.vue";

/** "no data" color */
let noDataColor = "#a0a0a0";

/** element refs */
const scroll = ref<HTMLDivElement>();
const element = ref<HTMLDivElement>();

type Props = {
  /** data */
  data?: Data;
  locations?: Locations;
  /** map of feature id to value */
  values?: Values["values"];
  /** value domain */
  min?: number;
  max?: number;
  /** map pan/zoom */
  lat: number;
  long: number;
  zoom: number;
  /** show/hide elements */
  showLegends: boolean;
  /** layer opacities */
  baseOpacity: number;
  dataOpacity: number;
  locationOpacity: number;
  /** tile providers for layers */
  base: string;
  /** color gradient id */
  gradient: string;
  /** scale props */
  flipGradient: boolean;
  scaleSteps: number;
  niceSteps: boolean;
  scalePower: number;
  /** number below which is treated as special "no-data" band */
  noData?: number;
  /** forced dimensions */
  width: number;
  height: number;
  /** filename for download */
  filename: string | string[];
};

const props = withDefaults(defineProps<Props>(), {
  data: () => ({ type: "FeatureCollection", features: [] }),
  locations: () => ({}),
  values: () => ({}),
  min: 0,
  max: 1,
  noData: 0,
});

type Emits = {
  "update:zoom": [Props["zoom"]];
  "update:lat": [Props["lat"]];
  "update:long": [Props["long"]];
};

const emit = defineEmits<Emits>();

type Slots = {
  "top-left": () => unknown;
  "top-right": () => unknown;
  "bottom-right": () => unknown;
};

defineSlots<Slots>();

/** elements to teleport legend template content to */
const topLeftLegend = ref<HTMLElement>();
const topRightLegend = ref<HTMLElement>();
const bottomRightLegend = ref<HTMLElement>();

/** element to teleport popup template content to */
const popup = ref<HTMLElement>();

/** properties of selected feature for popup */
const popupFeature = ref<GeoJsonProperties>();

/** https://leafletjs.com/reference.html#map-option */
const mapOptions: MapOptions = {
  zoomControl: false,
  attributionControl: false,
};

/** map object */
let map: L.Map | undefined;

/** create legend panel */
function createLegend(options: L.ControlOptions) {
  const Control = L.Control.extend({
    onAdd: () => document.createElement("div"),
  });
  const legend = new Control(options);
  map?.addControl(legend);
  return legend.getContainer();
}

/** set fine level of zoom snap, e.g. for tighter fit-bounds */
function fineZoom() {
  if (map) map.options.zoomSnap = 0.1;
}

/** set coarse level of zoom snap, to make track pad pinch zoom less frustrating */
async function coarseZoom() {
  /** wait for any in progress zoom to finish */
  await sleep();
  if (map) map.options.zoomSnap = 0.2;
}

/** get map layers by type */
function getLayers<T extends L.Layer = L.Layer>(
  pane: string,
  type: Function = L.Layer,
) {
  const layers: L.Layer[] = [];
  map?.eachLayer((layer) => {
    if (layer.options.pane === pane && layer instanceof type)
      layers.push(layer);
  });
  return layers as T[];
}

/** bind popup to layer */
function bindPopup(layer: L.Layer) {
  layer.bindPopup(() => "");
  layer.on("popupopen", async (event) => {
    const wrapper = event.popup
      .getElement()
      ?.querySelector<HTMLElement>(".leaflet-popup-content-wrapper");
    if (!wrapper) return;
    wrapper.innerHTML = "";
    popup.value = wrapper || undefined;
    /** wait for popup to teleport */
    await nextTick();
    popupFeature.value = event.sourceTarget.feature.properties;
    /** wait for popup to populate to full size before updating position */
    await nextTick();
    event.popup.update();
  });
  layer.on("popupclose", () => {
    /** unset popup */
    popup.value = undefined;
    popupFeature.value = undefined;
  });
}

const scale = computed(() => {
  /** get range of data (accounting for "no data" values) */
  const min = props.noData ? Math.max(props.min, props.noData) : props.min;
  const max = props.max;

  /** "nice", approximate number of steps */
  const nice = d3.ticks(min, max, props.scaleSteps);

  /** make sure steps always covers/contains range of values (min/max) */
  const step = d3.tickStep(min, max, props.scaleSteps);
  if (nice.at(0)! > min) nice.unshift(nice.at(0)! - step);
  if (nice.at(-1)! < max) nice.push(nice.at(-1)! + step);

  /** exact number of steps */
  const exact = d3
    .range(min, max, (max - min) / props.scaleSteps)
    .concat([max]);

  /** spaced list of points between min and max */
  let intervals = props.niceSteps ? nice : exact;

  /** make sure enough intervals */
  if (intervals.length < 3) intervals = [min, (min + max) / 2, max];

  /** range of intervals */
  const [lower = 0, upper = 1] = d3.extent(intervals);

  /** apply power */
  intervals = intervals.map((value) =>
    normalizedApply(value, lower, upper, (value) =>
      Math.pow(value, props.scalePower),
    ),
  );

  /** get gradient interpolator function from shorthand id/name */
  const gradient = getGradient(props.gradient);

  /** derive props for each step between points */
  const steps = d3.pairs(intervals).map(([lower, upper], index, array) => ({
    lower,
    upper,
    color: gradient(index / (array.length - 1)),
  }));

  /** reverse color values */
  const colors = steps.map((step) => step.color);
  if (props.flipGradient) {
    colors.reverse();
    steps.forEach((step, index) => (step.color = colors[index] || ""));
  }

  /** scale interpolator */
  const getColor = (value: number) =>
    props.noData && value <= props.noData
      ? noDataColor
      : d3.scaleQuantile<string>().domain(intervals).range(colors)(value);

  return { steps, getColor };
});

/** fit view to data layer content */
const fit = debounce(async () => {
  /** get bounding box of geojson data */
  let bounds = getLayers<L.GeoJSON>("data", L.GeoJSON)[0]?.getBounds();
  if (!bounds?.isValid()) return;

  /** get tight fit */
  fineZoom();
  /** reset zoom snap when zoom animation finishes */
  map?.once("zoomend", coarseZoom);

  /** default fit padding */
  let padding = { top: 0, left: 0, bottom: 0, right: 0 };

  /** make room for legends */
  if (props.showLegends) {
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (v: "top" | "bottom", h: "left" | "right") => {
      const { width, height } = getBbox(`.leaflet-${v}.leaflet-${h}`);
      if (height > width) padding[h] = Math.max(width, padding[h]);
      else padding[v] = Math.max(height, padding[v]);
    };
    padCorner("top", "left");
    padCorner("top", "right");
    padCorner("bottom", "left");
    padCorner("bottom", "right");
  }

  map?.fitBounds(bounds, {
    paddingTopLeft: [padding.left + 20, padding.top + 20],
    paddingBottomRight: [padding.right + 20, padding.bottom + 20],
  });
}, 200);

/** auto-fit when props change */
watch([() => props.showLegends, () => props.locations], fit, { deep: true });

/** when map container created */
onMounted(() => {
  if (!element.value) return;

  /** init map */
  map?.remove();
  map = L.map(element.value, mapOptions);

  /** manually make attribution again to specify position */
  L.control.attribution({ position: "bottomleft" }).addTo(map);

  /** add panes to map */
  map.createPane("base").style.zIndex = "0";
  map.createPane("data").style.zIndex = "1";
  map.createPane("locations").style.zIndex = "2";

  /** add legends to map and set elements to teleport slots into */
  topLeftLegend.value = createLegend({ position: "topleft" });
  topRightLegend.value = createLegend({ position: "topright" });
  bottomRightLegend.value = createLegend({ position: "bottomright" });

  /** update props from map pan/zoom */
  map.on("moveend", () => {
    if (!map) return;
    const { lat, lng } = map.getCenter();
    emit("update:lat", lat);
    emit("update:long", lng);
    emit("update:zoom", map.getZoom());
  });

  /** preserve fine-grain fitted zoom on drag */
  map.on("dragstart", fineZoom);
  /** reset zoom snap when done dragging */
  map.on("dragend", coarseZoom);
  coarseZoom();

  /** update stuff once map init'd */
  updateBase();
  updateData();
  updateLocations();
});

/** when map container destroyed */
onBeforeUnmount(() => {
  /** cleanup map on unmount */
  map?.remove();
});

/** update base layer */
function updateBase() {
  getLayers("base").forEach((layer) => layer.remove());
  const layer = L.tileLayer.provider(props.base, { pane: "base" });
  map?.addLayer(layer);
}

/** update base layer when props change */
watch(() => props.base, updateBase, { immediate: true });

/** update data layers */
function updateData() {
  getLayers("data").forEach((layer) => layer.remove());
  const layer = L.geoJSON(undefined, { pane: "data" });
  map?.addLayer(layer);
  layer.addData(props.data);
  bindPopup(layer);

  /** set feature static styles */
  layer.setStyle({
    weight: 1,
    color: "black",
    opacity: 1,
    fillOpacity: 1,
  });

  /** if no pan/zoom specified, fit view to content, */
  if (!props.lat && !props.long && !props.zoom) {
    fit();
  } else {
    /** otherwise, set view from props */
    updateView();
  }

  /** update stuff once layers init'd */
  updateColors();
  updateOpacities();
}

/** update map data layer when props change */
watch(() => props.data, updateData, { deep: true });

/** symbols (icon + label) associated with each location */
const symbols = computed(() => {
  let index = 0;
  return mapValues(props.locations, ({ label }) => {
    const icon = markerOptions[index++ % markerOptions.length];
    const image = icon?.options.iconUrl || "";
    return { label, icon, image };
  });
});

/** update location layers */
function updateLocations() {
  getLayers<L.GeoJSON>("locations", L.GeoJSON).forEach((layer) =>
    layer.remove(),
  );
  for (const [key, { features }] of Object.entries(props.locations)) {
    const icon = symbols.value[key]?.icon;
    const layer = L.geoJSON(undefined, {
      pointToLayer: (feature, coords) => {
        /** for point, display as marker */
        if (feature.geometry.type === "Point")
          return L.marker(coords, { icon, pane: "locations" });
        return L.layerGroup();
      },
    });
    bindPopup(layer);
    map?.addLayer(layer);
    layer.addData(features);
  }
}

/** update location layers when props change */
watch(() => props.locations, updateLocations, { deep: true });

/** auto-fit when map container element changes size */
let first = true;
useResizeObserver(element, () => {
  /** don't fit on page load (don't override url map view params) */
  if (first) return (first = false);
  map?.invalidateSize();
  fit();
});

/** update map pan/zoom */
function updateView() {
  map?.setView([props.lat || 0, props.long || 0], props.zoom || 1);
}

/** update map view when props change */
watch([() => props.lat, () => props.long, () => props.zoom], updateView);

/** update data feature colors */
function updateColors() {
  getLayers<L.GeoJSON>("data", L.GeoJSON).forEach((layer) =>
    layer.setStyle((feature) => ({
      fillColor: scale.value.getColor(
        props.values?.[feature?.properties.id]?.value || 0,
      ),
    })),
  );
}

/** update colors when data values or color scheme changes */
watch([() => props.values, scale], updateColors, {});

/** update layer opacities */
function updateOpacities() {
  if (!map) return;

  /** get layers */
  const base = map.getPane("base");
  const data = map.getPane("data");
  const locations = map.getPane("locations");

  /** set layer opacities */
  if (base) base.style.opacity = String(props.baseOpacity);
  if (data) data.style.opacity = String(props.dataOpacity);
  if (locations) locations.style.opacity = String(props.locationOpacity);
}

/** update opacities when props change */
watch(
  [
    () => props.baseOpacity,
    () => props.dataOpacity,
    () => props.locationOpacity,
  ],
  updateOpacities,
  {},
);

/** is measure a percent */
const percent = computed(() => isPercent(props.min, props.max));

/** whether element has scrollbars */
const scrollable = useScrollable(scroll);

/** enable/disable zooming by scrolling */
watch(scrollable, () => {
  if (!map) return;
  if (scrollable.value) map.scrollWheelZoom.disable();
  else map.scrollWheelZoom.enable();
});

/** actual client size */
const { width: actualWidth, height: actualHeight } = useElementSize(element);

/** download map as png */
async function download() {
  if (!element.value) return;

  /** upscale for better quality */
  const scale = window.devicePixelRatio;

  const blob = await domtoimage.toBlob(element.value, {
    width: actualWidth.value * scale,
    height: actualHeight.value * scale,
    style: {
      transform: `scale(${scale})`,
      transformOrigin: "top left",
    },
  });

  downloadPng(blob, props.filename);
}

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(element);
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scroll {
  flex-grow: 1;
  overflow: auto;
  box-shadow: var(--shadow);
}

.legend {
  display: flex;
  flex-direction: column;
  max-width: 250px;
  padding: 20px;
  gap: 20px;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

.legend:empty {
  display: none;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.steps {
  display: grid;
  grid-template-columns: 1.5em max-content max-content max-content;
  grid-auto-rows: 1.5em;
  place-items: center;
  width: fit-content;
  gap: 0 10px;
}

.steps svg {
  width: 100%;
}

.symbols {
  display: grid;
  grid-template-columns: auto auto;
  gap: 10px;
}

.symbols img {
  place-self: center;
  height: 1em;
}
</style>

<style>
.leaflet-container {
  font: inherit !important;
}

.leaflet-interactive:hover {
  filter: brightness(50%) saturate(0%);
  opacity: 0.5;
}

.leaflet-control-attribution {
  max-width: 500px;
  padding: 0.25em 0.5em;
  border-radius: var(--rounded) 0 0 0;
  background: var(--white);
  box-shadow: var(--shadow) !important;
  font: inherit;
  font-size: 0.8rem;
}

.leaflet-popup-content-wrapper {
  display: flex;
  flex-direction: column;
  width: max-content;
  max-width: 400px;
  padding: 20px 25px;
  gap: 10px;
  border-radius: var(--rounded);
  box-shadow: var(--shadow);
  font: inherit;
}

.leaflet-popup-content {
  width: unset !important;
  margin: 0;
}

.leaflet-popup-tip {
  width: 10px;
  height: 10px;
  margin: -5px auto 0 auto;
  padding: 0;
  box-shadow: unset;
}

/* https://github.com/Leaflet/Leaflet/issues/3994 */
.leaflet-fade-anim .leaflet-popup {
  transition: none;
}
</style>
