<template>
  <div
    ref="scrollElement"
    v-bind="$attrs"
    class="scroll"
    :style="{
      maxWidth: width ? width + 'px' : '',
      maxHeight: height ? height + 'px' : '',
    }"
  >
    <!-- map leaflet root -->
    <div
      ref="mapElement"
      :style="{
        width: width ? width + 'px' : '100%',
        height: height ? height + 'px' : '100%',
      }"
    />
  </div>

  <!-- top left legend -->
  <Teleport
    v-if="showLegends && topLeftLegend && scale.steps.length"
    :to="topLeftLegend"
  >
    <div v-stop class="legend">
      <slot name="top-left-upper" />

      <!-- scale key -->
      <div class="scale" :style="{ '--cols': scale.steps.length }">
        <div
          v-for="(step, key) of scale.steps"
          :key="key"
          v-tooltip="step.tooltip"
          class="scale-color"
          tabindex="0"
          :style="{ background: step.color }"
        />
        <div v-for="(step, key) of scale.steps" :key="key" class="scale-label">
          {{ step.label }}
        </div>
      </div>

      <slot name="top-left-lower" />
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
        <template v-for="(symbol, key) of symbols" :key="key">
          <img :src="symbol?.url" alt="" />
          <small>{{ symbol?.label }}</small>
        </template>
      </div>
    </div>
  </Teleport>

  <!-- bottom left legend -->
  <Teleport v-if="showLegends && bottomLeftLegend" :to="bottomLeftLegend">
    <div v-stop class="legend">
      <slot name="bottom-left" />
    </div>
  </Teleport>

  <!-- feature popup -->
  <Teleport v-if="popup && Object.keys(featureInfo).length" :to="popup">
    <slot :feature="featureInfo" name="popup" />
  </Teleport>
</template>

<script lang="ts">
type FeatureInfo = Record<string, unknown>;
</script>

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
import type { Feature, FeatureCollection, Geometry } from "geojson";
import L, { type MapOptions } from "leaflet";
import { cloneDeep, debounce, isEmpty, mapValues } from "lodash";
import { useElementSize, useFullscreen, useResizeObserver } from "@vueuse/core";
import { type Unit } from "@/api";
import { getGradient, gradientOptions } from "@/components/gradient";
import { getMarker, resetMarkers } from "@/components/markers";
import { baseOptions } from "@/components/tile-providers";
import { useScrollable } from "@/util/composables";
import { downloadPng } from "@/util/download";
import { formatValue, normalizedApply } from "@/util/math";
import { getBbox, sleep } from "@/util/misc";
import "leaflet/dist/leaflet.css";
import { capitalize } from "@/util/string";

/** "no data" color */
let noDataColor = "#a0a0a0";

/** "no data scale entry */
const noDataEntry = {
  value: "",
  label: "ND",
  color: noDataColor,
  tooltip: "No data, suppressed value, or 0",
};

/** element refs */
const scrollElement = ref<HTMLDivElement>();
const mapElement = ref<HTMLDivElement>();

type Props = {
  /** features */
  geometry?: FeatureCollection;
  locations?: Record<string, FeatureCollection>;
  /** map of geometry id to value */
  values?: Record<string, { value: number | string; [key: string]: unknown }>;
  /** value domain */
  min?: number | string;
  max?: number | string;
  unit?: Unit;
  /** map pan/zoom */
  lat?: number;
  long?: number;
  zoom?: number;
  /** show/hide elements */
  showLegends?: boolean;
  /** layer opacities */
  backgroundOpacity?: number;
  geometryOpacity?: number;
  locationOpacity?: number;
  /** tile provider */
  background?: string;
  /** color gradient id */
  gradient?: string;
  /** scale props */
  flipGradient?: boolean;
  scaleSteps?: number;
  niceSteps?: boolean;
  scalePower?: number;
  /** enumerated values for scale */
  scaleValues?: (number | string)[];
  /** forced dimensions */
  width?: number;
  height?: number;
  /** filename for download */
  filename?: string | string[];
};

const props = withDefaults(defineProps<Props>(), {
  geometry: () => ({ type: "FeatureCollection", features: [] }),
  locations: () => ({}),
  values: () => ({}),
  min: undefined,
  max: undefined,
  unit: undefined,
  lat: 0,
  long: 0,
  zoom: 1,
  showLegends: true,
  backgroundOpacity: 1,
  geometryOpacity: 0.75,
  locationOpacity: 1,
  background: baseOptions[0]!.id,
  gradient: gradientOptions[3]!.id,
  flipGradient: false,
  scaleSteps: 5,
  niceSteps: false,
  scalePower: 1,
  scaleValues: undefined,
  width: 0,
  height: 0,
  filename: "map",
});

type Emits = {
  "update:zoom": [Props["zoom"]];
  "update:lat": [Props["lat"]];
  "update:long": [Props["long"]];
  "update:no-data": [boolean];
};

const emit = defineEmits<Emits>();

type Slots = {
  "top-left-upper": () => unknown;
  "top-left-lower": () => unknown;
  "top-right": () => unknown;
  "bottom-right": () => unknown;
  "bottom-left": () => unknown;
  popup: ({ feature }: { feature: FeatureInfo }) => unknown;
};

defineSlots<Slots>();

/** elements to teleport legend template content to */
const topLeftLegend = ref<HTMLElement>();
const topRightLegend = ref<HTMLElement>();
const bottomRightLegend = ref<HTMLElement>();
const bottomLeftLegend = ref<HTMLElement>();

/** element to teleport popup template content to */
const popup = ref<HTMLElement>();

/** info about selected feature for popup */
const featureInfo = ref<FeatureInfo>({});

/** https://leafletjs.com/reference.html#map-option */
const mapOptions: MapOptions = {
  zoomControl: false,
  attributionControl: false,
  trackResize: false,
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
    popup.value =
      event.popup
        .getElement()
        ?.querySelector<HTMLElement>(".leaflet-popup-content-wrapper") ||
      undefined;
    if (!popup.value) return;
    /** wait for popup to teleport */
    await nextTick();

    /**
     * set info for selected feature. clone to avoid weird proxy linking
     * effects.
     */
    let info: FeatureInfo = cloneDeep(event.sourceTarget.feature.properties);
    const value = props.values?.[typeof info.id === "string" ? info.id : ""];
    if (value) info = { ...info, ...value };
    featureInfo.value = info;

    /** wait for popup to populate to full size before updating position */
    await nextTick();
    event.popup.update();
  });
  layer.on("popupclose", () => {
    /** unset popup */
    popup.value = undefined;
    featureInfo.value = {};
  });
}

/** close popups when data becomes stale */
watch(
  [() => props.geometry, () => props.locations, () => props.values],
  () => map?.closePopup(),
  { deep: true },
);

/** whether map has any "no data" geometry regions */
const noData = computed(
  () =>
    !props.geometry.features.every(
      (feature) => (feature.properties?.id ?? "") in props.values,
    ),
);

/** tell parent about "no data" */
watch(noData, () => emit("update:no-data", noData.value), { immediate: true });

/** scale object */
const scale = computed(() => {
  /** get gradient interpolator function from shorthand id/name */
  const gradient = getGradient(props.gradient);

  /** scale steps */
  const steps: ((
    | { value: number | string }
    | { lower: number; upper: number }
  ) & { label: string; color: string; tooltip: string })[] = [];

  /** map specific values to specific colors */
  if (props.scaleValues) {
    /** add "no data" entry */
    if (noData.value) steps.push(noDataEntry);

    /** explicit steps */
    steps.push(
      ...props.scaleValues.map((value, index, array) => {
        const percent = index / (array.length - 1);
        const label =
          typeof value === "number"
            ? formatValue(value, props.unit, true)
            : capitalize(value);
        return {
          value,
          label,
          color: gradient(props.flipGradient ? 1 - percent : percent),
          tooltip: label,
        };
      }),
    );

    /** explicit color */
    const getColor = (value?: number | string) =>
      steps.find((step) => ("value" in step ? step.value === value : undefined))
        ?.color ?? noDataColor;

    return { steps, getColor };
  } else if (
    /** continuous scale */
    !isEmpty(props.values) &&
    typeof props.min === "number" &&
    typeof props.max === "number" &&
    props.min !== props.max
  ) {
    /** get range of data */
    const min = props.min;
    const max = props.max;

    /** scale bands (spaced list of points between min and max) */
    let bands = [min, max];

    /** "nice", approximate number of steps */
    if (props.niceSteps) {
      bands = d3.ticks(min, max, props.scaleSteps);

      /** make sure steps always covers/contains range of values (min/max) */
      const step = d3.tickStep(min, max, props.scaleSteps);
      if (bands.at(0)! > min) bands.unshift(bands.at(0)! - step);
      if (bands.at(-1)! < max) bands.push(bands.at(-1)! + step);
    } else {
      /** exact number of steps */
      bands = d3.range(min, max, (max - min) / props.scaleSteps).concat([max]);
    }

    /** make sure enough bands */
    if (bands.length < 3) bands = [min, (min + max) / 2, max];

    /** range of bands */
    const [lower = 0, upper = 1] = d3.extent(bands);

    /** apply power */
    bands = bands.map((value) =>
      normalizedApply(value, lower, upper, (value) =>
        Math.pow(value, props.scalePower),
      ),
    );

    /** derive props for each step between points */
    steps.push(
      ...d3.pairs(bands).map(([lower, upper], index, array) => ({
        lower,
        upper,
        label:
          /** only add first and last labels */
          index === 0
            ? formatValue(min, props.unit, true)
            : index === array.length - 1
              ? formatValue(max, props.unit, true)
              : "",
        color: gradient(index / (array.length - 1)),
        tooltip: `${formatValue(lower, props.unit)} &ndash; ${formatValue(upper, props.unit)}`,
      })),
    );

    /** get colors (excluding "no data" entry) for scale range */
    const colors = steps.map((step) => step.color);

    /** reverse gradient colors */
    if (props.flipGradient) {
      colors.reverse();
      steps.forEach((step, index) => (step.color = colors[index] || ""));
    }

    /** add "no data" entry to start of list (after reversing performed) */
    if (noData.value) steps.unshift(noDataEntry);

    /** scale interpolator */
    const getColor = (value?: number | string) =>
      value === undefined || typeof value === "string"
        ? noDataColor
        : d3.scaleQuantile<string>().domain(bands).range(colors)(value);

    return { steps, getColor };
  } else {
    /** last resort fallback */
    return { steps: [], getColor: () => noDataColor };
  }
});

/** fit view to data layer content */
const fit = debounce(async () => {
  /** get bounding box of geojson data */
  let bounds = getLayers<L.GeoJSON>("geometry", L.GeoJSON)[0]?.getBounds();
  if (!bounds?.isValid()) return;

  /** get tight fit */
  fineZoom();
  /** reset zoom snap when zoom animation finishes */
  map?.once("zoomend", coarseZoom);

  /** default fit padding */
  let padding = { top: 0, left: 0, bottom: 0, right: 0 };

  /** make room for legends */
  if (props.showLegends) {
    const mapDimensions = map?.getContainer().getBoundingClientRect()!;
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (v: "top" | "bottom", h: "left" | "right") => {
      const { width, height } = getBbox(
        `.leaflet-${v}.leaflet-${h} .leaflet-control`,
      );
      if (mapDimensions?.width > mapDimensions?.height)
        padding[h] = Math.max(width, padding[h]);
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

/**
 * wait for autopan to finish and wait for spurious moveend events from
 * positioning tooltip to finish
 */
const onMoveEnd = debounce(() => {
  if (!map) return;
  const { lat, lng } = map.getCenter();
  emit("update:lat", lat);
  emit("update:long", lng);
  emit("update:zoom", map.getZoom());
}, 1000);

/** auto-fit when props change */
watch([() => props.showLegends, () => props.locations], fit, { deep: true });

/** when map container created */
onMounted(() => {
  if (!mapElement.value) return;

  /** init map */
  map?.remove();
  map = L.map(mapElement.value, mapOptions);

  /** manually make attribution again to specify position */
  L.control.attribution({ position: "bottomleft" }).addTo(map);

  /** add panes to map */
  map.createPane("background").style.zIndex = "0";
  map.createPane("geometry").style.zIndex = "1";
  map.createPane("locations").style.zIndex = "2";

  /** add legends to map and set elements to teleport slots into */
  topLeftLegend.value = createLegend({ position: "topleft" });
  topRightLegend.value = createLegend({ position: "topright" });
  bottomRightLegend.value = createLegend({ position: "bottomright" });
  bottomLeftLegend.value = createLegend({ position: "bottomleft" });

  /** update props from map pan/zoom */
  map.on("moveend", onMoveEnd);

  /** preserve fine-grain fitted zoom on drag */
  map.on("dragstart", fineZoom);
  /** reset zoom snap when done dragging */
  map.on("dragend", coarseZoom);
  coarseZoom();

  /** provide zoom level as css variable */
  map.on("zoomend", ({ target }) =>
    map?.getContainer().style.setProperty("--zoom", target._zoom),
  );

  /** update stuff once map init'd */
  updateBase();
  updateData();
  updateLocations();
});

/** when map container destroyed */
onBeforeUnmount(() => {
  /** cleanup map on unmount */
  fit.cancel();
  onMoveEnd.cancel();
});

/** update base layer */
function updateBase() {
  getLayers("background").forEach((layer) => layer.remove());
  const layer = L.tileLayer.provider(props.background, { pane: "background" });
  map?.addLayer(layer);
}

/** update base layer when props change */
watch(() => props.background, updateBase, { immediate: true });

/** update data layers */
function updateData() {
  getLayers("geometry").forEach((layer) => layer.remove());
  const layer = L.geoJSON(undefined, {
    pane: "geometry",
    onEachFeature:
      props.geometry.features.length < 100
        ? /** add feature labels */
          (feature: Feature<Geometry, FeatureInfo>) => {
            /** make sure label props exist */
            if (typeof feature.properties.label !== "string") return;
            if (typeof feature.properties.cent_lat !== "number") return;
            if (typeof feature.properties.cent_long !== "number") return;

            /** create label layer */
            const layer = L.marker(
              [feature.properties.cent_lat, feature.properties.cent_long],
              {
                pane: "geometry",
                icon: L.divIcon({
                  className: "geometry-label",
                  html: `<div>${feature.properties.label}</div>`,
                  iconSize: [0, 0],
                }),
              },
            );
            map?.addLayer(layer);
          }
        : undefined,
  });
  map?.addLayer(layer);
  layer.addData(props.geometry);

  /**
   * set feature static styles. can't use css class due to leaflet bugs.
   * https://github.com/leaflet/leaflet/issues/2662#issuecomment-2193684759
   */
  layer.setStyle({
    weight: 1,
    color: "black",
    fillOpacity: 1,
  });

  bindPopup(layer);

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
watch(() => props.geometry, updateData, { deep: true });

/** symbols (icon + label) associated with each location */
const symbols = computed(() => {
  resetMarkers();

  return mapValues(props.locations, (location, label) => {
    if (location.features[0]?.geometry.type === "Point")
      return { ...getMarker("point"), label };
    if (location.features[0]?.geometry.type === "Polygon")
      return { ...getMarker("area"), label };
  });
});

/** update location layers */
function updateLocations() {
  const layers = getLayers<L.GeoJSON>("locations", L.GeoJSON);
  layers.forEach((layer) => layer.remove());
  for (const [key, features] of Object.entries(props.locations)) {
    const { color, dash, icon } = symbols.value[key] ?? {};
    const layer = L.geoJSON(undefined, {
      pane: "locations",
      pointToLayer: (feature, coords) =>
        L.marker(coords, { icon, pane: "locations" }),
    });
    bindPopup(layer);
    map?.addLayer(layer);
    layer.addData(features);
    layer.setStyle({
      weight: 3,
      color,
      fillOpacity: 0,
      dashArray: dash,
    });
  }
}

/** update location layers when props change */
watch(() => props.locations, updateLocations, { deep: true });

/** when map element changes size */
useResizeObserver(mapElement, () => {
  map?.invalidateSize();
});

/** update map pan/zoom */
function updateView() {
  map?.setView([props.lat || 0, props.long || 0], props.zoom || 1);
}

/** update map view when props change */
watch([() => props.lat, () => props.long, () => props.zoom], updateView);

/** update data feature colors */
function updateColors() {
  getLayers<L.GeoJSON>("geometry", L.GeoJSON).forEach((layer) =>
    layer.setStyle((feature) => ({
      fillColor: scale.value.getColor(
        props.values?.[feature?.properties.id]?.value,
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
  const base = map.getPane("background");
  const data = map.getPane("geometry");
  const locations = map.getPane("locations");

  /** set layer opacities */
  if (base) base.style.opacity = String(props.backgroundOpacity);
  if (data) data.style.opacity = String(props.geometryOpacity);
  if (locations) locations.style.opacity = String(props.locationOpacity);
}

/** update opacities when props change */
watch(
  [
    () => props.backgroundOpacity,
    () => props.geometryOpacity,
    () => props.locationOpacity,
  ],
  updateOpacities,
  {},
);

/** whether element has scrollbars */
const scrollable = useScrollable(scrollElement);

/** enable/disable zooming by scrolling */
watch(scrollable, () => {
  if (!map) return;
  if (scrollable.value) map.scrollWheelZoom.disable();
  else map.scrollWheelZoom.enable();
});

/** actual client size */
const { width: actualWidth, height: actualHeight } = useElementSize(mapElement);

/** download map as png */
async function download() {
  if (!mapElement.value) return;

  /** upscale for better quality */
  const scale = window.devicePixelRatio;

  const blob = await domtoimage.toBlob(mapElement.value, {
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
const { toggle: fullscreen } = useFullscreen(mapElement);

/** highlight and zoom in on feature */
async function selectFeature(id: string) {
  if (!map) return;
  const layer = getLayers<L.Polygon>("geometry", L.Polygon).find(
    (layer) => layer.feature?.properties.id === id,
  );
  if (!layer) return;
  map.fitBounds(layer.getBounds());
  layer.setStyle({ fillColor: "var(--theme)" });
  /** zoom out a bit to give context of surroundings */
  map.zoomOut(1);
}

/** allow control from parent */
defineExpose({
  download,
  zoomIn: () => map?.zoomIn(),
  zoomOut: () => map?.zoomOut(),
  fit,
  fullscreen,
  selectFeature,
});
</script>

<style scoped>
.scroll {
  overflow: auto;
  box-shadow: var(--shadow);
}

.legend {
  display: flex;
  flex-direction: column;
  max-width: 250px;
  padding: 20px;
  gap: 10px;
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

.scale {
  display: grid;
  grid-template-rows: 20px;
  grid-template-columns: repeat(var(--cols), 1fr);
  justify-items: center;
  gap: 5px 0;
}

.scale-color {
  width: 100%;
  height: 100%;
}

.scale-label {
  max-width: 60px;
  padding: 0 5px;
  overflow: visible;
  text-align: center;
  overflow-wrap: break-word;
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
  font: inherit;
}

.leaflet-interactive {
  transition: fill-opacity var(--fast);
}

.leaflet-interactive:hover {
  fill-opacity: 0.25;
}

.leaflet-marker-icon {
  transition: opacity var(--fast);
}

.leaflet-marker-icon:hover {
  opacity: 0.25;
}

.leaflet-control-attribution {
  max-width: 500px;
  padding: 0.25em 0.5em;
  border-radius: var(--rounded) 0 0 0;
  background: var(--white);
  box-shadow: var(--shadow);
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
  display: none;
}

.leaflet-popup-tip {
  width: 10px;
  height: 10px;
  margin: -5px auto 0 auto;
  padding: 0;
  box-shadow: unset;
}

.leaflet-control {
  transition: opacity 0.5s;
}

.leaflet-container:has(.leaflet-popup)
  :is(.leaflet-control-container, .leaflet-control-container *) {
  pointer-events: none;
}

.leaflet-container:has(.leaflet-popup) .leaflet-control {
  opacity: 0;
}

/* https://github.com/Leaflet/Leaflet/issues/3994 */
.leaflet-fade-anim .leaflet-popup {
  transition: none !important;
}

.geometry-label {
  z-index: 999 !important;
}

.geometry-label > div {
  -webkit-text-stroke: calc(0.01 * pow(2, var(--zoom)) * 1px) white;
  paint-order: stroke;
  width: min-content;
  height: min-content;
  transform: translate(-50%, -50%);
  font-weight: var(--bold);
  font-size: calc(0.075 * pow(2, var(--zoom)) * 1px);
  line-height: 1;
  text-align: center;
  pointer-events: none;
}
</style>
