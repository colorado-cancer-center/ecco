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
import { debounce } from "lodash";
import { useElementSize, useFullscreen, useResizeObserver } from "@vueuse/core";
import type { Geometry } from "@/api";
import { getGradient } from "@/components/gradient";
import { downloadPng } from "@/util/download";
import { formatValue } from "@/util/math";
import { sleep } from "@/util/misc";
import "leaflet/dist/leaflet.css";
import {
  faCropSimple,
  faDownload,
  faExpand,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons";
import AppButton from "@/components/AppButton.vue";
import { useScrollable } from "@/util/composables";

// element refs
const scroll = ref<HTMLDivElement>();
const element = ref<HTMLDivElement>();

type Props = {
  // geojson
  geometry?: Geometry;
  // map pan/zoom
  lat?: number;
  long?: number;
  zoom?: number;
  // map of feature id to value
  values?: { [key: number]: number };
  // value domain
  min?: number;
  max?: number;
  // show/hide elements
  showLegend?: boolean;
  showDetails?: boolean;
  // layer opacities
  baseOpacity?: number;
  overlayOpacity?: number;
  dataOpacity?: number;
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
};

const props = withDefaults(defineProps<Props>(), {
  geometry: () => [],
  lat: undefined,
  long: undefined,
  zoom: undefined,
  values: () => ({}),
  min: 0,
  max: 0,
  showLegend: true,
  baseOpacity: 1,
  overlayOpacity: 1,
  dataOpacity: 0.75,
  base: "Stadia.AlidadeSmooth",
  overlays: () => [],
  gradient: "interpolateCool",
  flipGradient: false,
  scaleSteps: 5,
  niceSteps: true,
  width: 0,
  height: 0,
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
let map = L.map(document.createElement("div"), mapOptions);

// layer groups
let baseGroup = L.featureGroup();
let overlayGroup = L.featureGroup();
let dataLayer = L.geoJSON();

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

// when map container created
onMounted(() => {
  if (!element.value) return;

  // init map
  map.remove();
  map = L.map(element.value, mapOptions);

  // add layer groups
  baseGroup.addTo(map);
  overlayGroup.addTo(map);
  dataLayer.addTo(map);

  // add control to map and set element to teleport legend template into
  legendTeleport.value = new Control({ position: "bottomleft" })
    .addTo(map)
    .getContainer();

  // update props from map pan/zoom
  map.on("moveend", () => {
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
  updateGeometry();
});

// when map container destroyed
onBeforeUnmount(() => {
  // cleanup map on unmount
  map.remove();
});

// update base layer of map
function updateBase() {
  baseGroup.clearLayers();
  baseGroup.addLayer(L.tileLayer.provider(props.base));
}

// update base layer when props change
watch(() => props.base, updateBase, { immediate: true });

// update overlay layers of map
function updateOverlays() {
  overlayGroup.clearLayers();
  for (const overlay of props.overlays)
    overlayGroup.addLayer(L.tileLayer.provider(overlay));
}

// update overlay layers when props change
watch(() => props.overlays, updateOverlays, { immediate: true, deep: true });

// fit view to data layer content
const fit = debounce(async () => {
  // get bounding box of geojson data
  let bounds = dataLayer.getBounds();

  if (!bounds.isValid()) return;

  // get tight fit
  fineZoom();
  // reset zoom snap when zoom animation finishes
  map.once("zoomend", coarseZoom);

  map.fitBounds(bounds, {
    // make room for legend
    paddingTopLeft: [props.showLegend ? 220 : 20, 20],
  });
}, 200);

// auto-fit when legend enabled/disabled
watch(() => props.showLegend, fit);

// auto-fit when map container element changes size
let first = true;
useResizeObserver(element, () => {
  if (first) return (first = false);
  map?.invalidateSize();
  fit();
});

// update map pan/zoom
function updateView() {
  map.setView([props.lat || 0, props.long || 0], props.zoom || 1);
}

// update map view when props change
watch([() => props.lat, () => props.long, () => props.zoom], updateView);

// update geometry of map
function updateGeometry() {
  // reset data layer
  dataLayer.clearLayers();

  // re-load geometry
  for (const feature of props.geometry) dataLayer.addData(feature);

  // set feature static styles
  dataLayer.setStyle({
    weight: 0.5,
    color: "black",
  });

  // attach popups
  dataLayer.bindPopup(() => "");
  dataLayer.on("popupopen", async (event) => {
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
  dataLayer.on("popupclose", () => {
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

// update map geometry when props change
watch(() => props.geometry, updateGeometry, { immediate: true, deep: true });

// update data feature colors
function updateColors() {
  dataLayer.setStyle((feature) => ({
    fillColor: scale.value(props.values?.[feature?.properties.id] || 0),
  }));
}

// update colors when data values or color scheme changes
watch([() => props.values, scale], updateColors, {
  immediate: true,
});

// update layer opacities
function updateOpacities() {
  baseGroup.eachLayer((layer) => {
    if (layer instanceof L.TileLayer) layer.setOpacity(props.baseOpacity);
  });
  overlayGroup.eachLayer((layer) => {
    if (layer instanceof L.TileLayer) layer.setOpacity(props.overlayOpacity);
  });
  dataLayer.setStyle({
    opacity: props.dataOpacity,
    fillOpacity: props.dataOpacity,
  });
}

// update opacities when props change
watch(
  [
    () => props.baseOpacity,
    () => props.overlayOpacity,
    () => props.dataOpacity,
  ],
  updateOpacities,
  {
    immediate: true,
  },
);

// whether element has scrollbars
const scrollable = useScrollable(scroll);

// enable/disable zooming by scrolling
watch(scrollable, () => {
  if (scrollable.value) map.scrollWheelZoom.disable();
  else map.scrollWheelZoom.enable();
});

// actual client size of map
const { width: actualWidth, height: actualHeight } = useElementSize(element);

// download map as png
async function download(filename: string | string[]) {
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
  downloadPng(blob, filename);
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
  display: inline-grid;
  grid-template-columns: 1.5em max-content max-content max-content;
  grid-auto-rows: 1.5em;
  align-items: center;
  justify-items: flex-end;
  gap: 0 10px;
}

.steps svg {
  width: 100%;
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
