<template>
  <div class="container">
    <div ref="scroll" class="scroll">
      <div
        ref="element"
        class="map"
        :style="{
          width: width ? width + 'px' : '100%',
          height: height ? height + 'px' : '100%',
        }"
      />
    </div>

    <div class="controls">
      <AppButton
        v-tooltip="'Download current map view as PNG'"
        :icon="faDownload"
        :accent="true"
        @click="download"
        >Download Map</AppButton
      >
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
      />
      <AppButton
        v-tooltip="'View map in full screen'"
        :icon="faExpand"
        @click="fullscreen"
      />
    </div>

    <Teleport v-if="legendTeleport && $slots.heading" :to="legendTeleport">
      <div class="legend" @mousedown.stop>
        <div class="legend-slot">
          <slot name="heading" />
        </div>

        <div v-if="$slots.details" class="legend-slot">
          <slot name="details" />
        </div>

        <div class="steps">
          <template v-for="(step, index) of [...steps].reverse()" :key="index">
            <svg viewBox="0 0 1 1">
              <rect x="0" y="0" width="1" height="1" :fill="step.color" />
            </svg>
            <span>{{ step.lower }}</span>
            <span>&ndash;</span>
            <span>{{ step.upper }}</span>
          </template>
        </div>

        <div v-if="Object.keys(symbols).length" class="symbols">
          <template v-for="(symbol, index) of symbols" :key="index">
            <img :src="symbol.image" alt="" />
            <small>{{ symbol.label }}</small>
          </template>
        </div>
      </div>
    </Teleport>

    <Teleport v-if="popupTeleport && popupFeature" :to="popupTeleport">
      <div class="mini-table">
        <span>Name</span>
        <span>{{ popupFeature.name }}</span>
        <span>FIPS</span>
        <span>{{ popupFeature.id }}</span>
        <span>Value</span>
        <span>{{ formatValue(values[popupFeature.id], min, max) }}</span>
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
import type { Geometry, Markers } from "@/api";
import AppButton from "@/components/AppButton.vue";
import { getGradient } from "@/components/gradient";
import { markerOptions } from "@/components/markers";
import { useScrollable } from "@/util/composables";
import { downloadPng } from "@/util/download";
import { formatValue } from "@/util/math";
import { sleep } from "@/util/misc";
import "leaflet/dist/leaflet.css";

// element refs
const scroll = ref<HTMLDivElement>();
const element = ref<HTMLDivElement>();

type Props = {
  // data
  geometry?: Geometry;
  markers?: Markers;
  // map of feature id to value
  values?: { [key: number]: number };
  // value domain
  min?: number;
  max?: number;
  // map pan/zoom
  lat?: number;
  long?: number;
  zoom?: number;
  // show/hide elements
  showLegend?: boolean;
  showDetails?: boolean;
  // layer opacities
  baseOpacity?: number;
  dataOpacity?: number;
  markerOpacity?: number;
  // tile providers for layers
  base?: string;
  overlays?: string[];
  // color gradient id
  gradient?: string;
  // scale props
  flipGradient?: boolean;
  scaleSteps?: number;
  niceSteps?: boolean;
  // forced dimensions
  width?: number;
  height?: number;
  // filename for download
  filename?: string | string[];
};

const props = withDefaults(defineProps<Props>(), {
  geometry: () => [],
  markers: () => ({}),
  values: () => ({}),
  min: 0,
  max: 1,
  lat: undefined,
  long: undefined,
  zoom: undefined,
  showLegend: true,
  baseOpacity: 1,
  dataOpacity: 0.75,
  markerOpacity: 1,
  base: "Stadia.AlidadeSmooth",
  overlays: () => [],
  gradient: "interpolateCool",
  flipGradient: false,
  scaleSteps: 5,
  niceSteps: true,
  width: 0,
  height: 0,
  filename: "map",
});

type Emits = {
  "update:zoom": [Props["zoom"]];
  "update:lat": [Props["lat"]];
  "update:long": [Props["long"]];
};

const emit = defineEmits<Emits>();

type Slots = {
  heading: () => unknown;
  details: () => unknown;
};

defineSlots<Slots>();

// element to teleport legend template content to
const legendTeleport = ref<HTMLElement>();

// element to teleport popup template content to
const popupTeleport = ref<HTMLElement>();

// properties of selected feature for popup
const popupFeature = ref<GeoJsonProperties>();

// https://leafletjs.com/reference.html#map-option
const mapOptions: MapOptions = { zoomControl: false };

// leaflet map object
let map: L.Map | undefined;

// custom control class
const Control = L.Control.extend({
  onAdd: () => document.createElement("div"),
});

// set fine level of zoom snap, e.g. for tighter fit-bounds
function fineZoom() {
  if (map) map.options.zoomSnap = 0.1;
}

// set coarse level of zoom snap, to make track pad pinch zoom not frustrating
async function coarseZoom() {
  await sleep();
  if (map) map.options.zoomSnap = 1;
}

// get gradient interpolator function from shorthand id/name
const _gradient = computed(() => getGradient(props.gradient));

// steps to split scale into
const steps = computed(() => {
  // generate spaced list of points between min and max
  const intervals = props.niceSteps
    ? // "nice", approximate number
      d3
        .scaleLinear()
        .domain([props.min, props.max])
        .nice()
        .ticks(props.scaleSteps)
    : // exact number
      d3
        .range(props.min, props.max, (props.max - props.min) / props.scaleSteps)
        .concat([props.max]);

  // get range of points
  const [min = 0, max = 1] = d3.extent(intervals);

  // normalize value from [min, max] to [0, 1] or [1, 0] for mapping to color
  function normalize(value: number) {
    return (value - min) / (max - min);
  }

  // derive props for each step between points
  const steps = d3.pairs(intervals).map(([lower, upper], index, array) => ({
    lower: formatValue(lower, props.min, props.max),
    upper: formatValue(upper, props.min, props.max),
    color: _gradient.value(
      normalize(
        index === 0
          ? lower
          : index === array.length - 1
          ? upper
          : (lower + upper) / 2,
      ),
    ),
  }));

  // flip color values
  if (props.flipGradient) {
    const colors = steps.map((step) => step.color);
    colors.reverse();
    steps.forEach((step, index) => (step.color = colors[index] || ""));
  }

  return steps;
});

// scale interpolator
const scale = computed(() => {
  const range = steps.value.map((step) => step.color);
  return d3.scaleQuantize<string>().domain([props.min, props.max]).range(range);
});

// fit view to data layer content
const fit = debounce(async () => {
  // get bounding box of geojson data
  let bounds = getLayers<L.GeoJSON>("data", L.GeoJSON)[0]?.getBounds();

  if (!bounds?.isValid()) return;

  // get tight fit
  fineZoom();
  // reset zoom snap when zoom animation finishes
  map?.once("zoomend", coarseZoom);

  map?.fitBounds(bounds, {
    // make room for legend
    paddingTopLeft: [props.showLegend ? 220 : 20, 20],
  });
}, 200);

// auto-fit when legend enabled/disabled
watch(() => props.showLegend, fit);

// when map container created
onMounted(() => {
  if (!element.value) return;

  // init map
  map?.remove();
  map = L.map(element.value, mapOptions);

  // add panes to map
  map.createPane("base").style.zIndex = "0";
  map.createPane("data").style.zIndex = "1";
  map.createPane("overlay").style.zIndex = "2";
  map.createPane("markers").style.zIndex = "3";

  // add control to map and set element to teleport legend template into
  legendTeleport.value = new Control({ position: "topleft" })
    .addTo(map)
    .getContainer();

  // update props from map pan/zoom
  map.on("moveend", () => {
    if (!map) return;
    const { lat, lng } = map.getCenter();
    emit("update:lat", lat);
    emit("update:long", lng);
    emit("update:zoom", map.getZoom());
  });

  // preserve fine-grain fitted zoom on drag
  map.on("dragstart", fineZoom);
  // reset zoom snap when done dragging
  map.on("dragend", coarseZoom);

  // update stuff once map init'd
  updateBase();
  updateData();
  updateMarkers();
});

// when map container destroyed
onBeforeUnmount(() => {
  // cleanup map on unmount
  map?.remove();
});

// func to get map layers, since leaflet doesn't have one
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

// update base layer
function updateBase() {
  getLayers("base").forEach((layer) => layer.remove());
  const layer = L.tileLayer.provider(props.base, { pane: "base" });
  map?.addLayer(layer);
}

// update base layer when props change
watch(() => props.base, updateBase, { immediate: true });

// update data layers
function updateData() {
  // update layer
  getLayers("data").forEach((layer) => layer.remove());
  const layer = L.geoJSON(undefined, { pane: "data" });
  map?.addLayer(layer);

  // re-load geojson
  for (const feature of props.geometry) layer.addData(feature);

  // set feature static styles
  layer.setStyle({
    weight: 1,
    color: "black",
    opacity: 1,
    fillOpacity: 1,
  });

  // attach popups
  layer.bindPopup(() => "");
  layer.on("popupopen", async (event) => {
    // wait for teleported slot to render
    await nextTick();
    const wrapper = event.popup
      .getElement()
      ?.querySelector<HTMLElement>(".leaflet-popup-content-wrapper");
    if (wrapper) wrapper.innerHTML = "";
    popupTeleport.value = wrapper || undefined;
    popupFeature.value = event.sourceTarget.feature.properties;
    await nextTick();
    event.popup.update();
  });
  layer.on("popupclose", () => {
    popupTeleport.value = undefined;
    popupFeature.value = undefined;
  });

  // if no pan/zoom specified, fit view to content,
  if (!props.lat && !props.long && !props.zoom) fit();
  // otherwise, set view from props
  else updateView();

  // update stuff once layers init'd
  updateColors();
  updateOpacities();
}

// update map data layer when props change
watch(() => props.geometry, updateData, { immediate: true, deep: true });

// icons associated with each marker key
const symbols = computed(() => {
  let index = 0;
  return mapValues(props.markers, ({ label }) => {
    const icon = markerOptions[index++ % markerOptions.length];
    const image = icon?.options.iconUrl || "";
    return { label, icon, image };
  });
});

// update marker layers
function updateMarkers() {
  getLayers("markers").forEach((layer) => layer.remove());
  for (const [key, value] of Object.entries(props.markers)) {
    const icon = symbols.value[key]?.icon;
    for (const { coords } of value.points) {
      const [long, lat] = coords;
      const marker = L.marker([lat, long], { icon, pane: "markers" });
      map?.addLayer(marker);
    }
  }
}

// update marker layers when props change
watch(() => props.markers, updateMarkers, { immediate: true, deep: true });

// auto-fit when map container element changes size
let first = true;
useResizeObserver(element, () => {
  if (first) return (first = false);
  map?.invalidateSize();
  fit();
});

// update map pan/zoom
function updateView() {
  map?.setView([props.lat || 0, props.long || 0], props.zoom || 1);
}

// update map view when props change
watch([() => props.lat, () => props.long, () => props.zoom], updateView);

// update data feature colors
function updateColors() {
  getLayers<L.GeoJSON>("data", L.GeoJSON).forEach((layer) =>
    layer.setStyle((feature) => ({
      fillColor: scale.value(props.values?.[feature?.properties.id] || 0),
    })),
  );
}

// update colors when data values or color scheme changes
watch([() => props.values, scale], updateColors, {
  immediate: true,
});

// update layer opacities
function updateOpacities() {
  if (!map) return;

  // get layers
  const base = map.getPane("base");
  const data = map.getPane("data");
  const markers = map.getPane("markers");

  // set layer opacities
  if (base) base.style.opacity = String(props.baseOpacity);
  if (data) data.style.opacity = String(props.dataOpacity);
  if (markers) markers.style.opacity = String(props.markerOpacity);
}

// update opacities when props change
watch(
  [() => props.baseOpacity, () => props.dataOpacity, () => props.markerOpacity],
  updateOpacities,
  {
    immediate: true,
  },
);

// whether element has scrollbars
const scrollable = useScrollable(scroll);

// enable/disable zooming by scrolling
watch(scrollable, () => {
  if (!map) return;
  if (scrollable.value) map.scrollWheelZoom.disable();
  else map.scrollWheelZoom.enable();
});

// actual client size
const { width: actualWidth, height: actualHeight } = useElementSize(element);

// download map as png
async function download() {
  const el = element.value;
  if (!el) return;
  // upscale for better quality
  const scale = window.devicePixelRatio;
  const blob = await domtoimage.toBlob(el, {
    width: actualWidth.value * scale,
    height: actualHeight.value * scale,
    style: {
      transform: `scale(${scale})`,
      transformOrigin: "top left",
    },
  });
  downloadPng(blob, props.filename);
}

// toggle fullscreen on element
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
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.legend {
  display: flex;
  flex-direction: column;
  width: min-content;
  padding: 20px;
  gap: 20px;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

.legend-slot {
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow-wrap: break-word;
}

.steps {
  display: grid;
  grid-template-columns: 1.5em max-content max-content max-content;
  grid-auto-rows: 1.5em;
  align-items: center;
  justify-items: flex-end;
  gap: 0 10px;
}

.steps svg {
  width: 100%;
}

.symbols {
  display: grid;
  grid-template-columns: 1em auto;
  gap: 10px;
}

.symbols img {
  position: relative;
  top: 0.15em;
}
</style>

<style>
.leaflet-container {
  font: inherit !important;
}

.leaflet-control-attribution {
  padding: 0.25em 0.5em;
  border-radius: var(--rounded) 0 0 0;
  background: var(--white);
  box-shadow: var(--shadow) !important;
  font-size: 0.8rem;
}

.leaflet-popup-content-wrapper {
  width: max-content;
  padding: 20px 25px;
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
