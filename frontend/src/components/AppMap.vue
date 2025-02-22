<template>
  <div ref="scrollElement" v-bind="$attrs" class="scroll">
    <!-- map root -->
    <Map.OlMap
      ref="mapRef"
      :style="{
        width: width ? width + 'px' : '100%',
        height: height ? height + 'px' : '100%',
      }"
      :controls="[]"
    >
      <!-- viewport -->
      <Map.OlView
        ref="viewRef"
        :center="center"
        :zoom="zoom"
        projection="EPSG:4326"
        @change:center="onCenter"
        @change:resolution="onZoom"
      />

      <!-- background layer -->
      <Layers.OlTileLayer :opacity="backgroundOpacity">
        <Sources.OlSourceXyz :url="backgroundUrl" cross-origin="anonymous" />
      </Layers.OlTileLayer>

      <!-- geometry layer -->
      <Layers.OlVectorLayer>
        <Sources.OlSourceVector ref="geometryRef" :features="features">
          <Map.OlFeature
            v-for="(feature, key) in features"
            :key="key"
            :properties="feature.getProperties()"
          >
            <!-- https://github.com/MelihAltintas/vue3-openlayers/issues/410 -->
            <Styles.OlStyle
              :key="JSON.stringify(scale.steps) + geometryOpacity"
            >
              <Styles.OlStyleStroke color="black" />
              <Styles.OlStyleFill
                :color="
                  feature.get('id') === highlight
                    ? getCssVar('--theme')
                    : scale.getColor(
                        values?.[feature.get('id')]?.value,
                        geometryOpacity,
                      )
                "
              />
            </Styles.OlStyle>
          </Map.OlFeature>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

      <!-- label layer -->
      <Layers.OlVectorLayer name="labels">
        <Sources.OlSourceVector>
          <Map.OlFeature v-for="(feature, key) in features" :key="key">
            <Geometries.OlGeomPoint
              :coordinates="[feature.get('cent_long'), feature.get('cent_lat')]"
            />
            <Styles.OlStyle>
              <Styles.OlStyleText :text="feature.get('label')" v-bind="font" />
            </Styles.OlStyle>
          </Map.OlFeature>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

      <!-- interactions -->
      <Interactions.OlInteractionSelect
        :key="Math.random()"
        :condition="pointerMove"
        :layers="(layer) => layer.get('name') !== 'labels'"
      >
        <Styles.OlStyle>
          <Styles.OlStyleFill :color="getCssVar('--theme')" />
        </Styles.OlStyle>
      </Interactions.OlInteractionSelect>

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
        <div v-if="$slots['bottom-right']" class="legend bottom-right">
          <slot name="bottom-right" />
        </div>
        <div v-if="$slots['bottom-left']" class="legend bottom-left">
          <slot name="bottom-left" />
        </div>
      </template>
    </Map.OlMap>
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
import { computed, onMounted, ref, watch, watchEffect } from "vue";
import {
  Geometries,
  Interactions,
  Layers,
  Map,
  Sources,
  Styles,
} from "vue3-openlayers";
import * as d3 from "d3";
import domtoimage from "dom-to-image-more";
import type { FeatureCollection } from "geojson";
import { capitalize, isEmpty } from "lodash";
import { pointerMove } from "ol/events/condition";
import GeoJSON from "ol/format/GeoJSON";
import type { ObjectEvent } from "ol/Object";
import { useElementSize, useFullscreen } from "@vueuse/core";
import { type Unit } from "@/api";
import { getGradient, gradientOptions } from "@/components/gradient";
import { backgroundOptions } from "@/components/tile-providers";
import { downloadPng } from "@/util/download";
import { formatValue, normalizedApply } from "@/util/math";
import { getBbox, getCssVar, sleep, toHex, waitFor } from "@/util/misc";

const scrollElement = ref<HTMLDivElement>();
const mapRef = ref<InstanceType<typeof Map.OlMap>>();
const mapElement = computed(() => mapRef.value?.map.getTargetElement());
const viewRef = ref<InstanceType<typeof Map.OlView>>();
const geometryRef = ref<InstanceType<typeof Sources.OlSourceVector>>();

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

/** combined lat/long coords */
const center = computed(() => [props.long, props.lat]);

/** on center change */
function onCenter(event: ObjectEvent) {
  const [long, lat] = event.target.getCenter();
  emit("update:lat", lat);
  emit("update:long", long);
}

/** on zoom change */
function onZoom(event: ObjectEvent) {
  const newZoom = event.target.getZoom();
  if (newZoom) emit("update:zoom", newZoom);
}

/** parse geojson features */
const features = computed(() => new GeoJSON().readFeatures(props.geometry));

/** font style attributes */
const font: InstanceType<typeof Styles.OlStyleText>["$props"] = computed(
  () => ({
    font: `600 ${props.zoom * 1.5}px 'Roboto Flex'`,
    fill: "black",
    stroke: { color: "white", width: 2 },
    overflow: true,
    declutterMode: "obstacle",
  }),
);

/** background tile url template */
const backgroundUrl = computed(
  () =>
    backgroundOptions.find((option) => option.id === props.background)
      ?.template ?? "",
);

/** whether map has any "no data" geometry regions */
const noData = computed(
  () =>
    !props.geometry.features.every(
      (feature) => (feature.properties?.id ?? "") in props.values,
    ),
);

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
    const getColor = (value?: number | string, opacity?: number) =>
      toHex(
        steps.find((step) =>
          "value" in step ? step.value === value : undefined,
        )?.color ?? noDataColor,
        opacity,
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
    const getColor = (value?: number | string, opacity?: number) =>
      value === undefined || typeof value === "string"
        ? noDataColor
        : toHex(
            d3.scaleQuantile<string>().domain(bands).range(colors)(value),
            opacity,
          );

    return { steps, getColor };
  } else {
    /** last resort fallback */
    return { steps: [], getColor: () => noDataColor };
  }
});

/** change cursor to indicate click-ability */
watchEffect(() => {
  const map = mapRef.value?.map;
  /** https://stackoverflow.com/questions/26022029/how-to-change-the-cursor-on-hover-in-openlayers-3 */
  map?.on("pointermove", ({ pixel }) => {
    const hit = map.hasFeatureAtPixel(pixel);
    map.getTargetElement().style.cursor = hit ? "pointer" : "";
  });
});

function zoomIn() {
  viewRef.value?.adjustZoom(1);
}

function zoomOut() {
  viewRef.value?.adjustZoom(-1);
}

/** fit view to geometry layer content */
function fit() {
  if (!viewRef.value || !geometryRef.value) return;

  /** get bounding box of content */
  const extent = geometryRef.value.source.getExtent();

  /** default fit padding */
  let padding = { top: 0, left: 0, bottom: 0, right: 0 };

  /** make room for legends */
  if (props.showLegends) {
    const mapDimensions = mapElement.value?.getBoundingClientRect()!;
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (v: "top" | "bottom", h: "left" | "right") => {
      const { width, height } = getBbox(`.legend.${v}-${h}`);
      if (mapDimensions?.width > mapDimensions?.height)
        padding[h] = Math.max(width, padding[h]);
      else padding[v] = Math.max(height, padding[v]);
    };
    padCorner("top", "left");
    padCorner("top", "right");
    padCorner("bottom", "left");
    padCorner("bottom", "right");
  }

  /** check if valid extent (can be infinities if no features) */
  if (extent && extent.every((value) => Number.isFinite(value))) {
    const { top, right, bottom, left } = padding;
    viewRef.value.fit(extent, { padding: [top, right, bottom, left] });
  }
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
    /** wait for features to be loaded, rendered,s parsed */
    await waitFor(() => geometryRef.value?.source.getFeatures().length);
    /** fit view to content */
    fit();
  }
});

/** toggle fullscreen on element */
const { toggle: fullscreen } = useFullscreen(scrollElement);

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
    style: { transform: `scale(${scale})`, transformOrigin: "top left" },
  });

  downloadPng(blob, props.filename);
}

/** highlight and zoom in on feature */
watch(
  [() => props.highlight, () => props.geometry, viewRef],
  () => {
    if (!props.highlight || !props.geometry || !viewRef.value) return;
    /** lookup feature by id */
    const feature = features.value.find(
      (feature) => feature.get("id") === props.highlight,
    );
    if (!feature) return;
    /** fit view to feature bounds */
    const extent = feature.getGeometry()?.getExtent();
    if (!extent) return;
    viewRef.value.fit(extent);
    /** zoom out a bit to give context of surroundings */
    viewRef.value?.adjustZoom(-1);
  },
  { immediate: true, deep: true },
);

/** allow control from parent */
defineExpose({
  zoomIn,
  zoomOut,
  fit,
  fullscreen,
  download,
});
</script>

<style scoped>
.scroll {
  position: relative;
  overflow: auto;
  box-shadow: var(--shadow);
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

.symbols img {
  place-self: center;
  height: 1em;
}
</style>
