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

    <!-- top right legend -->
    <Teleport v-if="showLegends && topRightLegend" :to="topRightLegend">
      <div class="legend" @mousedown.stop>
        <slot name="top-right" />
      </div>
    </Teleport>

    <!-- top left legend -->
    <Teleport v-if="showLegends && topLeftLegend" :to="topLeftLegend">
      <div class="legend legend-tight" @mousedown.stop>
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

        <slot name="top-left" />
      </div>
    </Teleport>

    <!-- bottom left legend -->
    <Teleport
      v-if="showLegends && bottomLeftLegend"
      :to="bottomLeftLegend"
      class="test"
    >
      <div class="legend legend-tight" @mousedown.stop>
        <slot name="bottom-left" />

        <div v-if="Object.keys(symbols).length" class="symbols">
          <template v-for="(symbol, index) of symbols" :key="index">
            <img :src="symbol.image" alt="" />
            <small>{{ symbol.label }}</small>
          </template>
        </div>
      </div>
    </Teleport>

    <Teleport v-if="popup && popupFeature" :to="popup">
      <!-- county/tract popup -->
      <div v-if="popupFeature.name && popupFeature.id" class="mini-table">
        <span>Name</span>
        <span>{{ popupFeature.name }}</span>
        <span>FIPS</span>
        <span>{{ popupFeature.id }}</span>
        <span>Value</span>
        <span>{{ formatValue(values[popupFeature.id], min, max) }}</span>
      </div>

      <!-- overlay popup -->
      <div v-if="popupFeature.info" v-html="popupFeature.info"></div>
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
import type { Data, Overlays } from "@/api";
import AppButton from "@/components/AppButton.vue";
import { getGradient } from "@/components/gradient";
import { markerOptions } from "@/components/markers";
import { useScrollable } from "@/util/composables";
import { downloadPng } from "@/util/download";
import { formatValue } from "@/util/math";
import { getBbox, sleep } from "@/util/misc";
import "leaflet/dist/leaflet.css";

/** element refs */
const scroll = ref<HTMLDivElement>();
const element = ref<HTMLDivElement>();

type Props = {
  /** data */
  data?: Data;
  overlays?: Overlays;
  /** map of feature id to value */
  values?: { [key: number]: number };
  /** value domain */
  min?: number;
  max?: number;
  /** map pan/zoom */
  lat?: number;
  long?: number;
  zoom?: number;
  /** show/hide elements */
  showLegends?: boolean;
  /** layer opacities */
  baseOpacity?: number;
  dataOpacity?: number;
  overlayOpacity?: number;
  /** tile providers for layers */
  base?: string;
  /** color gradient id */
  gradient?: string;
  /** scale props */
  flipGradient?: boolean;
  scaleSteps?: number;
  niceSteps?: boolean;
  /** forced dimensions */
  width?: number;
  height?: number;
  /** filename for download */
  filename?: string | string[];
};

const props = withDefaults(defineProps<Props>(), {
  data: () => ({ type: "FeatureCollection", features: [] }),
  overlays: () => ({}),
  values: () => ({}),
  min: 0,
  max: 1,
  lat: undefined,
  long: undefined,
  zoom: undefined,
  showLegends: true,
  baseOpacity: 1,
  dataOpacity: 0.75,
  overlayOpacity: 1,
  base: "Stadia.AlidadeSmooth",
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
  /** top right legend */
  "top-right": () => unknown;
  /** top left legend */
  "top-left": () => unknown;
  /** bottom left legend */
  "bottom-left": () => unknown;
};

defineSlots<Slots>();

/** elements to teleport legend template content to */
const topLeftLegend = ref<HTMLElement>();
const topRightLegend = ref<HTMLElement>();
const bottomLeftLegend = ref<HTMLElement>();

/** element to teleport popup template content to */
const popup = ref<HTMLElement>();

/** properties of selected feature for popup */
const popupFeature = ref<GeoJsonProperties>();

/** https://leafletjs.com/reference.html#map-option */
const mapOptions: MapOptions = { zoomControl: false };

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

/** set coarse level of zoom snap, to make track pad pinch zoom not frustrating */
async function coarseZoom() {
  /** wait for any in progress zoom to finish */
  await sleep();
  if (map) map.options.zoomSnap = 0.5;
}

/** steps to split scale into */
const steps = computed(() => {
  /** generate spaced list of points between min and max */
  const intervals = props.niceSteps
    ? /** "nice", approximate number */
      d3
        .scaleLinear()
        .domain([props.min, props.max])
        .nice()
        .ticks(props.scaleSteps)
    : /** exact number */
      d3
        .range(props.min, props.max, (props.max - props.min) / props.scaleSteps)
        .concat([props.max]);

  /** get range of points */
  const [min = 0, max = 1] = d3.extent(intervals);

  /** normalize value from [min, max] to [0, 1] or [1, 0] for mapping to color */
  function normalize(value: number) {
    return (value - min) / (max - min);
  }

  /** get gradient interpolator function from shorthand id/name */
  const gradient = getGradient(props.gradient);

  /** derive props for each step between points */
  const steps = d3.pairs(intervals).map(([lower, upper], index, array) => ({
    lower: formatValue(lower, props.min, props.max),
    upper: formatValue(upper, props.min, props.max),
    color: gradient(
      normalize(
        index === 0
          ? lower
          : index === array.length - 1
          ? upper
          : (lower + upper) / 2,
      ),
    ),
  }));

  /** reverse color values */
  if (props.flipGradient) {
    const colors = steps.map((step) => step.color);
    colors.reverse();
    steps.forEach((step, index) => (step.color = colors[index] || ""));
  }

  return steps;
});

/** scale interpolator */
const scale = computed(() =>
  d3
    .scaleQuantize<string>()
    .domain([props.min, props.max])
    .range(steps.value.map((step) => step.color)),
);

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
  let padding = { top: 20, left: 20, bottom: 20, right: 20 };

  /** make room for legends */
  if (props.showLegends) {
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (v: "top" | "bottom", h: "left" | "right") => {
      const { width, height } = getBbox(`.leaflet-${v}.leaflet-${h}`);
      if (height > width) padding[h] = Math.max(width, padding[h]);
      else padding[v] = Math.max(height, padding[v]);
    };
    padCorner("top", "right");
    padCorner("top", "left");
    padCorner("bottom", "left");
  }

  map?.fitBounds(bounds, {
    paddingTopLeft: [padding.left, padding.top],
    paddingBottomRight: [padding.right, padding.bottom],
  });
}, 200);

/** auto-fit when props change */
watch([() => props.showLegends, () => props.overlays], fit, { deep: true });

/** when map container created */
onMounted(() => {
  if (!element.value) return;

  /** init map */
  map?.remove();
  map = L.map(element.value, mapOptions);

  /** add panes to map */
  map.createPane("base").style.zIndex = "0";
  map.createPane("data").style.zIndex = "1";
  map.createPane("overlays").style.zIndex = "2";

  /** add legends to map and set elements to teleport slots into */
  topRightLegend.value = createLegend({ position: "topright" });
  topLeftLegend.value = createLegend({ position: "topleft" });
  bottomLeftLegend.value = createLegend({ position: "bottomleft" });

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
  updateOverlays();
});

/** when map container destroyed */
onBeforeUnmount(() => {
  /** cleanup map on unmount */
  map?.remove();
});

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
    if (wrapper) wrapper.innerHTML = "";
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
  /** update layers */
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
  if (!props.lat && !props.long && !props.zoom) fit();
  /** otherwise, set view from props */ else updateView();

  /** update stuff once layers init'd */
  updateColors();
  updateOpacities();
}

/** update map data layer when props change */
watch(() => props.data, updateData, { deep: true });

/** symbols (icon + label) associated with each overlay */
const symbols = computed(() => {
  let index = 0;
  return mapValues(props.overlays, ({ label }) => {
    const icon = markerOptions[index++ % markerOptions.length];
    const image = icon?.options.iconUrl || "";
    return { label, icon, image };
  });
});

/** update overlay layers */
function updateOverlays() {
  getLayers<L.GeoJSON>("overlays", L.GeoJSON).forEach((layer) =>
    layer.remove(),
  );
  for (const [key, { features }] of Object.entries(props.overlays)) {
    const icon = symbols.value[key]?.icon;
    const layer = L.geoJSON(undefined, {
      pointToLayer: (feature, coords) => {
        /** for point, display as marker */
        if (feature.geometry.type === "Point")
          return L.marker(coords, { icon });
        return L.layerGroup();
      },
      pane: "overlays",
    });
    bindPopup(layer);
    map?.addLayer(layer);
    layer.addData(features);
  }
}

/** update overlay layers when props change */
watch(() => props.overlays, updateOverlays, { deep: true });

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
      fillColor: scale.value(props.values?.[feature?.properties.id] || 0),
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
  const overlays = map.getPane("overlays");

  /** set layer opacities */
  if (base) base.style.opacity = String(props.baseOpacity);
  if (data) data.style.opacity = String(props.dataOpacity);
  if (overlays) overlays.style.opacity = String(props.overlayOpacity);
}

/** update opacities when props change */
watch(
  [
    () => props.baseOpacity,
    () => props.dataOpacity,
    () => props.overlayOpacity,
  ],
  updateOpacities,
  {},
);

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
}

.legend {
  display: flex;
  flex-direction: column;
  width: max-content;
  max-width: 300px;
  padding: 20px;
  gap: 5px;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

.legend:empty {
  display: none;
}

.legend-tight {
  max-width: 200px;
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

.leaflet-right {
  text-align: right;
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
