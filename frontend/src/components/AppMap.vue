<template>
  <div ref="scrollElement" v-bind="$attrs" class="scroll">
    <div
      ref="frameElement"
      :style="{
        width: width ? width + 'px' : '100%',
        height: height ? height + 'px' : '100%',
      }"
    >
      <!-- map root  -->
      <div ref="mapElement" class="map" />

      <!-- legends -->
      <template v-if="showLegends">
        <div
          v-if="$slots['top-left-upper'] || $slots['top-left-lower']"
          class="legend top-left"
        >
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
            <div
              v-for="(step, key) of scale.steps"
              :key="key"
              class="scale-label"
            >
              {{ step.label }}
            </div>
          </div>

          <slot name="top-left-lower" />
        </div>
        <div v-if="$slots['top-right']" class="legend top-right">
          <slot name="top-right" />
        </div>
        <div
          v-if="$slots['bottom-right'] || !isEmpty(symbols)"
          class="legend bottom-right"
        >
          <slot name="bottom-right" />

          <!-- symbol key -->
          <div v-if="!isEmpty(symbols)" class="symbols">
            <template v-for="(symbol, label) of symbols" :key="label">
              <template v-if="symbol">
                <div class="symbol" v-html="symbol.html" />
                <small>{{ label }}</small>
              </template>
            </template>
          </div>
        </div>
        <div v-if="$slots['bottom-left']" class="legend bottom-left">
          <slot name="bottom-left" />
        </div>
      </template>

      <div class="attribution" v-html="attribution" />
    </div>
  </div>
</template>

<script lang="ts">
type FeatureInfo = Record<string, unknown>;

/** "no data" color */
const noDataColor = "#a0a0a0";

/** "no data scale entry */
export const noDataEntry = {
  value: "",
  label: "ND",
  color: noDataColor,
  tooltip: "No data or suppressed value",
} as const;
</script>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, watchEffect } from "vue";
import * as d3 from "d3";
import domtoimage from "dom-to-image-more";
import type { FeatureCollection } from "geojson";
import { capitalize, isEmpty, mapValues } from "lodash";
import { Feature, Map, MapBrowserEvent, View } from "ol";
import { pointerMove } from "ol/events/condition";
import type { FeatureLike } from "ol/Feature";
import GeoJSON from "ol/format/GeoJSON";
import { Point } from "ol/geom";
import Select from "ol/interaction/Select";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import { XYZ } from "ol/source";
import VectorSource from "ol/source/Vector";
import { Fill, Icon, Stroke, Style, Text } from "ol/style";
import { useElementSize, useFullscreen } from "@vueuse/core";
import { type Unit } from "@/api";
import { getGradient, gradientOptions } from "@/components/gradient";
import { backgroundOptions } from "@/components/tile-providers";
import { downloadPng } from "@/util/download";
import { formatValue, normalizedApply } from "@/util/math";
import { forceHex, getBbox, getCssVar, sleep, waitFor } from "@/util/misc";
import { getMarkers } from "./markers";

const scrollElement = ref<HTMLDivElement>();
const frameElement = ref<HTMLDivElement>();
const mapElement = ref<HTMLDivElement>();

const theme = forceHex(getCssVar("--theme"));

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
  /** id of feature to highlight and zoom in on */
  highlight?: string;
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
  zoom: 0,
  showLegends: true,
  backgroundOpacity: 1,
  geometryOpacity: 0.75,
  locationOpacity: 1,
  background: backgroundOptions[0]!.id,
  gradient: gradientOptions[3]!.id,
  flipGradient: false,
  scaleSteps: 5,
  niceSteps: false,
  scalePower: 1,
  scaleValues: undefined,
  width: 0,
  height: 0,
  filename: "map",
  highlight: "",
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

/** scale object */
const scale = computed(() => {
  /** map 0-1 percent to color */
  const gradient = (percent: number) => {
    /** get gradient interpolator function from shorthand id/name */
    const gradient = getGradient(props.gradient);
    /** reverse */
    if (props.flipGradient) percent = 1 - percent;
    /** get color */
    return gradient(percent);
  };

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
        const label =
          typeof value === "number"
            ? formatValue(value, props.unit, true)
            : capitalize(value);
        return {
          value,
          label,
          color: gradient(index / (array.length - 1)),
          tooltip: label,
        };
      }),
    );

    /** explicit color */
    const getColor = (value?: number | string) =>
      forceHex(
        steps.find((step) =>
          "value" in step ? step.value === value : undefined,
        )?.color ?? noDataColor,
      );

    return { steps, getColor };
  } else if (
    /** map continuous values to discrete colors */
    /** (if we have needed and valid values) */
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

    /** add "no data" entry to start of list */
    if (noData.value) steps.unshift(noDataEntry);

    /** scale interpolator */
    const getColor = (value?: number | string) =>
      value === undefined || typeof value === "string"
        ? noDataColor
        : forceHex(
            d3.scaleQuantile<string>().domain(bands).range(colors)(value),
          );

    return { steps, getColor };
  } else {
    /** last resort fallback */
    return { steps: [], getColor: () => noDataColor };
  }
});

/** map object */
const map = new Map({ controls: [] });

/** update map root element */
watchEffect(() => map.setTarget(mapElement.value));

/** view object */
const view = new View({
  projection: "EPSG:4326",
  /** prevent extra zoom change events from causing recursive update error */
  smoothExtentConstraint: false,
  smoothResolutionConstraint: false,
});

/** add view to map */
watchEffect(() => map.setView(view));

/** update view center */
watchEffect(() => view.setCenter([props.long, props.lat]));
/** update view zoom */
watchEffect(() => view.setZoom(props.zoom));

/** on view pan */
view.on("change:center", () => {
  const center = view.getCenter();
  if (!center) return;
  emit("update:lat", center[1]);
  emit("update:long", center[0]);
});

/** on view zoom */
view.on("change:resolution", () => {
  const zoom = view.getZoom();
  if (!zoom) return;
  emit("update:zoom", zoom);
});

/** background source object */
const backgroundSource = new XYZ();
/** background layer object */
const backgroundLayer = new TileLayer({ source: backgroundSource });

/** attribution html */
const attribution = ref("");

/** update background layer url template */
watchEffect(() => {
  /** https://openlayers.org/en/latest/examples/reusable-source.html#:~:text=source.refresh */
  backgroundSource.refresh();
  /** look up full option details */
  const option = backgroundOptions.find(
    (option) => option.id === props.background,
  );
  if (!option) return;
  backgroundSource.setUrl(option.template ?? "");
  attribution.value = option.attribution;
});

/** update background layer opacity */
watchEffect(() => backgroundLayer.setOpacity(props.backgroundOpacity));

/** geometry source object */
const geometrySource = new VectorSource();
/** geometry layer object */
const geometryLayer = new VectorLayer({ source: geometrySource });

/** parse geometry features */
const geometryFeatures = computed(() =>
  new GeoJSON().readFeatures(props.geometry),
);

/** update geometry layer source */
watchEffect(() => {
  geometrySource.clear();
  geometrySource.addFeatures(geometryFeatures.value);
});

/** update geometry styles */
watchEffect((onCleanup) => {
  /** get reactive values in root of watch so they can be auto-tracked */
  const getColor = scale.value.getColor;
  const values = props.values;
  const highlight = props.highlight;

  /** generate styles per feature */
  const style =
    (hover = false) =>
    (feature: FeatureLike) =>
      new Style({
        stroke: new Stroke({ color: "black", width: hover ? 4 : 1 }),
        fill: new Fill({
          color:
            feature.get("id") === highlight
              ? theme
              : getColor(values?.[feature.get("id")]?.value),
        }),
        zIndex: hover ? 1 : 0,
      });

  /** base styles */
  geometryLayer.setStyle(style());

  /** hover styles */
  const hover = new Select({
    condition: pointerMove,
    style: style(true),
    /** don't count other layers, e.g. labels, in hover */
    layers: [geometryLayer],
  });
  map.addInteraction(hover);
  onCleanup(() => map.removeInteraction(hover));
});

/** update geometry layer opacity */
watchEffect(() => geometryLayer.setOpacity(props.geometryOpacity));

/** label source object */
const labelSource = new VectorSource();
/** label layer object */
const labelLayer = new VectorLayer({
  source: labelSource,
  style: (feature) =>
    new Style({
      text: new Text({
        text: feature.get("label"),
        font: `600 ${(view.getZoom() ?? 8) * 2}px 'Roboto Flex'`,
        stroke: new Stroke({ color: "white", width: 2 }),
        overflow: true,
      }),
    }),
});

/** update label layer source */
watchEffect(() => {
  labelSource.clear();
  labelSource.addFeatures(
    geometryFeatures.value.map(
      (feature) =>
        new Feature({
          label: feature.get("label"),
          geometry: new Point([
            feature.get("cent_long"),
            feature.get("cent_lat"),
          ]),
        }),
    ),
  );
});

/** update label layer opacity */
watchEffect(() => labelLayer.setOpacity(props.geometryOpacity));

/** parse location features */
const locationFeatures = computed(() => {
  const reader = new GeoJSON();
  return mapValues(props.locations, (value, location) => {
    /** parse geojson */
    const features = reader.readFeatures(value);

    for (const feature of features) {
      const symbol = symbols.value[location];
      if (!symbol) continue;

      /** add extra props */
      for (const [key, value] of Object.entries(symbol))
        feature.set(key, value);

      /** define icon object here instead of on more frequent style update */
      feature.set("icon", new Icon({ src: symbol.url, width: 16, height: 16 }));
      feature.set(
        "iconHover",
        new Icon({ src: symbol.url, width: 16, height: 16, color: "black" }),
      );
    }

    return features;
  });
});

/** locations source object */
const locationsSource = new VectorSource();
/** locations layer object */
const locationsLayer = new VectorLayer({ source: locationsSource });

/** update locations layer source */
watchEffect(() => {
  locationsSource.clear();
  locationsSource.addFeatures(Object.values(locationFeatures.value).flat());
});

/** update locations styles */
watchEffect((onCleanup) => {
  /** generate styles per feature */
  const style =
    (hover = false) =>
    (feature: FeatureLike) =>
      new Style({
        fill: new Fill({
          color: hover ? feature.get("color") + "20" : "transparent",
        }),
        stroke: new Stroke({
          color: feature.get("color"),
          width: hover ? 4 : 2,
          lineDash: feature.get("dash"),
        }),
        image: hover ? feature.get("iconHover") : feature.get("icon"),
        zIndex: hover ? 2 : 1,
      });

  /** base styles */
  locationsLayer.setStyle(style());
  /** hover styles */
  const hover = new Select({
    condition: pointerMove,
    style: style(true),
    /** don't count other layers, e.g. labels, in hover */
    layers: [locationsLayer],
  });
  map.addInteraction(hover);
  onCleanup(() => map.removeInteraction(hover));
});

/** update locations layer opacity */
watchEffect(() => locationsLayer.setOpacity(props.locationOpacity));

/** symbols (icon + label) associated with each location */
const symbols = computed(() =>
  getMarkers(
    Object.entries(props.locations).map(([label, location]) => [
      label,
      location.features[0]?.geometry.type ?? "",
    ]),
  ),
);

/** change cursor to indicate click-ability */
watchEffect((onCleanup) => {
  /** https://stackoverflow.com/questions/26022029/how-to-change-the-cursor-on-hover-in-openlayers-3 */
  const listener = ({ pixel }: MapBrowserEvent<any>) => {
    const hit = map.hasFeatureAtPixel(pixel);
    map.getTargetElement().style.cursor = hit ? "pointer" : "";
  };
  map.on("pointermove", listener);
  onCleanup(() => map.un("pointermove", listener));
});

/** add layers to map */
watchEffect(() =>
  map.setLayers([backgroundLayer, geometryLayer, labelLayer, locationsLayer]),
);

/** whether map has any "no data" geometry regions */
const noData = computed(
  () =>
    !props.geometry.features.every(
      (feature) => (feature.properties?.id ?? "") in props.values,
    ),
);

/** programmatic zoom in */
function zoomIn() {
  view.adjustZoom(1);
}

/** programmatic zoom out */
function zoomOut() {
  view.adjustZoom(-1);
}

/** map client size */
const { width: mapWidth, height: mapHeight } = useElementSize(frameElement);

/** fit view to geometry layer content */
function fit() {
  /** get bounding box of content */
  const extent = geometrySource.getExtent();

  /** check if valid extent (can be infinities if no features) */
  if (!extent || extent.some((value) => !Number.isFinite(value))) return;

  /** default fit padding */
  let padding = { top: 0, left: 0, bottom: 0, right: 0 };

  /** make room for legends */
  if (props.showLegends) {
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (v: "top" | "bottom", h: "left" | "right") => {
      let { width, height } = getBbox(`.legend.${v}-${h}`);
      width += 20;
      height += 20;
      if (mapWidth.value > mapHeight.value)
        padding[h] = Math.max(width, padding[h]);
      else padding[v] = Math.max(height, padding[v]);
    };
    padCorner("top", "left");
    padCorner("top", "right");
    padCorner("bottom", "left");
    padCorner("bottom", "right");
  }

  const { top, right, bottom, left } = padding;
  view.fit(extent, { padding: [top, right, bottom, left] });
}

/** auto-fit when props change */
watch(
  [() => props.showLegends, () => props.locations],
  /** wait for legends render */
  () => sleep().then(fit),
  { deep: true },
);

onMounted(async () => {
  /** if not highlighting specific feature */
  if (props.highlight) return;

  /** if no pan/zoom specified */
  if (!props.lat || !props.long || !props.zoom) {
    /** wait for features to be loaded, rendered/parsed */
    await waitFor(() => geometrySource.getFeatures().length);
    /** fit view to content */
    fit();
  }
});

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(scrollElement);

/** download map as png */
async function download() {
  if (!frameElement.value) return;

  /** upscale for better quality */
  const scale = window.devicePixelRatio;

  /** convert to image */
  const blob = await domtoimage.toBlob(frameElement.value, {
    width: mapWidth.value * scale,
    height: mapHeight.value * scale,
    style: { transform: `scale(${scale})`, transformOrigin: "top left" },
  });

  downloadPng(blob, props.filename);
}

/** highlight and zoom in on feature */
watch(
  [() => props.highlight, () => props.geometry],
  async () => {
    if (!props.highlight || !props.geometry) return;
    /** lookup feature by id */
    const feature = geometryFeatures.value.find(
      (feature) => feature.get("id") === props.highlight,
    );
    if (!feature) return;
    /** get feature bounds */
    const extent = feature.getGeometry()?.getExtent();
    if (!extent) return;
    /** wait for view to be attached to map */
    await waitFor(() => !!map.getView());
    /** fit view to feature bounds */
    view.fit(extent);
    /** zoom out a bit to give context of surroundings */
    view.adjustZoom(-1);
  },
  { immediate: true, deep: true },
);

/** allow control from parent */
defineExpose({ zoomIn, zoomOut, fit, fullscreen, download });

/** clean up objects */
onUnmounted(() => {
  map.dispose();
  view.dispose();
  backgroundLayer.dispose();
  geometryLayer.dispose();
});
</script>

<style scoped>
.scroll {
  position: relative;
  overflow: auto;
  box-shadow: var(--shadow);
}

.map {
  width: 100%;
  height: 100%;
}

.legend {
  display: flex;
  z-index: 9;
  position: absolute;
  flex-direction: column;
  max-width: 250px;
  padding: 20px;
  gap: 10px;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
  --spacing: 10px;
}

.top-left {
  top: var(--spacing);
  left: var(--spacing);
}

.top-right {
  top: var(--spacing);
  right: var(--spacing);
}

.bottom-right {
  right: var(--spacing);
  bottom: var(--spacing);
}

.bottom-left {
  bottom: var(--spacing);
  left: var(--spacing);
}

.legend:empty {
  display: none;
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

.symbol {
  display: contents;
}

.symbol > * {
  place-self: center;
  width: 1em;
  height: 1em;
}

.attribution {
  position: absolute;
  bottom: 0;
  left: 0;
  max-width: 50%;
  padding: 2px 5px;
  background: color-mix(in srgb, var(--white), transparent 25%);
  font-size: 12px;
  text-wrap: balance;
}
</style>
