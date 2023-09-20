<template>
  <div
    ref="element"
    class="map"
    :style="{
      width: width ? width + 'px' : '100%',
      height: height ? height + 'px' : '100%',
    }"
  />

  <Teleport v-if="legendTeleport && showLegend" :to="legendTeleport">
    <div class="legend" @mousedown.stop>
      <div class="header">
        <slot name="legend" />
      </div>

      <div class="steps">
        <template v-for="(step, index) of legendSteps" :key="index">
          <svg viewBox="0 0 1 1">
            <rect x="0" y="0" width="1" height="1" :fill="step.color" />
          </svg>
          <span>{{ step.start }}</span>
          <span>&ndash;</span>
          <span>{{ step.end }}</span>
        </template>
      </div>
    </div>
  </Teleport>

  <Teleport v-if="popupTeleport && popupFeature" :to="popupTeleport">
    <div class="popup">
      <span>Name</span>
      <span>{{ popupFeature.name }}</span>
      <span>FIPS</span>
      <span>{{ popupFeature.id }}</span>
      <span>Value</span>
      <span>{{ formatValue(values[popupFeature.id] || 0) }}</span>
    </div>
  </Teleport>
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
import L, { type MapOptions, type TileLayerOptions } from "leaflet";
import { debounce, round } from "lodash";
import { useElementSize, useResizeObserver } from "@vueuse/core";
import type { Geometry } from "@/api";
import { gradientOptions, type GradientFunc } from "@/components/gradient";
import { downloadPng } from "@/util/download";
import "leaflet/dist/leaflet.css";

// ref to root element
const element = ref<HTMLDivElement>();

type Props = {
  // map pan/zoom
  lat?: number;
  long?: number;
  zoom?: number;
  // geojson
  geometry?: Geometry;
  // show/hide legend
  showLegend?: boolean;
  // value domain
  min?: number;
  max?: number;
  // map of feature id to value
  values?: { [key: number]: number };
  // number of scale steps
  steps?: number;
  // color gradient id
  gradient?: string;
  // reverse direction of gradient
  flipGradient?: boolean;
  // forced dimensions
  width?: number;
  height?: number;
  // layer opacities
  baseOpacity?: number;
  dataOpacity?: number;
};

const props = withDefaults(defineProps<Props>(), {
  lat: undefined,
  long: undefined,
  zoom: undefined,
  geometry: () => [],
  showLegend: true,
  min: 0,
  max: 0,
  values: () => ({}),
  steps: 5,
  gradient: "interpolateCool",
  flipGradient: false,
  width: 0,
  height: 0,
  baseOpacity: 1,
  dataOpacity: 0.75,
});

type Emits = {
  "update:zoom": [Props["zoom"]];
  "update:lat": [Props["lat"]];
  "update:long": [Props["long"]];
};

const emit = defineEmits<Emits>();

// https://leafletjs.com/reference.html#map-option
const mapOptions: MapOptions = {
  // preferCanvas: true,
  zoomSnap: 0.1,
};

// https://leafletjs.com/reference.html#layer-option
const layerOptions: TileLayerOptions = {
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
};

// open street map data
const urlTemplate = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";

// leaflet map object
let map: L.Map | null = null;

// base layer of open street map data
const baseLayer = L.tileLayer(urlTemplate, layerOptions);

// layer for our own geojson data
let dataLayer = L.geoJSON();

// element to teleport legend template content to
const legendTeleport = ref<HTMLElement>();

// element to teleport popup template content to
const popupTeleport = ref<HTMLElement>();

// properties of selected feature for popup
const popupFeature = ref<GeoJsonProperties>();

onMounted(() => {
  if (!element.value) return;

  // init map
  map = L.map(element.value, mapOptions);

  // disable default zoom controls
  map.removeControl(map.zoomControl);

  // add layers
  baseLayer.addTo(map);
  dataLayer.addTo(map);

  // custom control class
  const Control = L.Control.extend({
    onAdd: () => document.createElement("div"),
  });

  // add control to map and set element to teleport legend template into
  legendTeleport.value = new Control({ position: "bottomleft" })
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

  // update stuff once map init'd
  updateGeometry();
});

onBeforeUnmount(() => {
  if (!map) return;
  // cleanup map on unmount
  map.remove();
});

// fit view to data layer content
const fit = debounce(function () {
  if (!map || !dataLayer) return;
  map.fitBounds(dataLayer.getBounds(), {
    // make room for legend
    paddingTopLeft: [props.showLegend ? 250 : 0, 0],
  });
}, 300);

// auto-fit when legend enabled/disabled
watch(() => props.showLegend, fit);

// auto-fit when map container element changes size
useResizeObserver(element, () => {
  map?.invalidateSize();
  fit();
});

// update map pan/zoom
function updateView() {
  if (!map) return;
  map.setView([props.lat || 0, props.long || 0], props.zoom || 1);
}

// update map view when props change
watch([() => props.lat, () => props.long, () => props.zoom], updateView);

// update geometry of map
function updateGeometry() {
  if (!map) return;

  // reset data layer
  dataLayer.clearLayers();

  // re-load geometry
  for (const feature of props.geometry) dataLayer.addData(feature);

  // set feature static styles
  dataLayer.setStyle(() => ({
    weight: 0.5,
    color: "black",
  }));

  // attach popups
  dataLayer.bindPopup(() => "xxxxxxxxxxxxxxxxxxxxxxxxxx");
  dataLayer.on("popupopen", async (event) => {
    // wait for
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

// scale interpolator
const scale = computed(() =>
  d3
    .scaleLinear()
    .domain([props.min, props.max])
    .range(props.flipGradient ? [1, 0] : [0, 1]),
);

// get gradient interpolator function from shorthand id/name
const gradientFunc = computed<GradientFunc>(
  () =>
    gradientOptions.find((option) => option.id === props.gradient)?.func ||
    d3.interpolateCool,
);

// update feature colors
function updateColors() {
  dataLayer.setStyle((feature) => ({
    fillColor: gradientFunc.value(
      scale.value(props.values?.[feature?.properties.id] || 0),
    ),
  }));
}

// update colors when data values or color scheme changes
watch([() => props.values, scale, gradientFunc], updateColors, {
  immediate: true,
});

// update layer opacities
function updateOpacities() {
  baseLayer.setOpacity(props.baseOpacity);
  dataLayer.setStyle({ fillOpacity: props.dataOpacity });
}

// update opacities when props change
watch([() => props.baseOpacity, () => props.dataOpacity], updateOpacities, {
  immediate: true,
});

// format map data value
function formatValue(value: number): string {
  if (props.min >= 0 && props.max <= 1) return round(value * 100, 1) + "%";
  else return value.toLocaleString(undefined, { notation: "compact" });
}

// legend steps
const legendSteps = computed(() => {
  const ticks = scale.value.nice().ticks(props.steps);

  // map spaced ticks to ranges and colors
  return ticks.slice(0, -1).map((value, index, array) => ({
    // use actual min for first
    start: formatValue(index === 0 ? props.min : value),
    // use actual max for last
    end: formatValue(
      index === array.length - 1 ? props.max : ticks[index + 1] || value,
    ),
    color: gradientFunc.value(scale.value(value)),
  }));
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

// zoom map in one step
function zoomIn() {
  map?.zoomIn();
}

// zoom map out one step
function zoomOut() {
  map?.zoomOut();
}

// allow parent to funcs
defineExpose({ download, fit, zoomIn, zoomOut });
</script>

<style scoped>
.legend {
  display: flex;
  flex-direction: column;
  max-width: 15rem;
  padding: 20px;
  gap: 20px;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

.header {
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

.popup {
  display: grid;
  grid-template-columns: auto auto;
  gap: 10px;
}

.popup span:nth-child(odd) {
  font-weight: var(--bold);
}
</style>

<style>
.leaflet-container {
  font: inherit !important;
}

.leaflet-layer {
  filter: saturate(0);
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
