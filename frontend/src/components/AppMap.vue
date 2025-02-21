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
      <Map.OlView
        ref="viewRef"
        :center="center"
        :zoom="zoom"
        projection="EPSG:4326"
        @change:center="onCenter"
        @change:resolution="onZoom"
      />

      <Layers.OlTileLayer :opacity="backgroundOpacity">
        <Sources.OlSourceXyz :url="backgroundUrl" />
      </Layers.OlTileLayer>

      <Layers.OlVectorLayer :opacity="geometryOpacity">
        <Sources.OlSourceVector ref="geometryRef" :features="features">
          <Map.OlFeature
            v-for="(feature, key) in features"
            :key="key"
            :properties="feature.getProperties()"
          >
            <Styles.OlStyle>
              <Styles.OlStyleStroke color="black" />
              <Styles.OlStyleFill
                :color="feature.get('id') === highlight ? 'black' : noDataColor"
              />
            </Styles.OlStyle>
          </Map.OlFeature>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

      <Interactions.OlInteractionSelect :condition="pointerMove">
        <Styles.OlStyle>
          <Styles.OlStyleFill color="black" />
        </Styles.OlStyle>
      </Interactions.OlInteractionSelect>

      <template v-if="showLegends">
        <div class="legend top-left">
          <slot name="top-left-upper" />
          <slot name="top-left-lower" />
        </div>
        <div class="legend top-right">
          <slot name="top-right" />
        </div>
        <div class="legend bottom-right">
          <slot name="bottom-right" />
        </div>
        <div class="legend bottom-left">
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
import { Interactions, Layers, Map, Sources, Styles } from "vue3-openlayers";
import domtoimage from "dom-to-image";
import type { FeatureCollection } from "geojson";
import { pointerMove } from "ol/events/condition";
import GeoJSON from "ol/format/GeoJSON";
import type { ObjectEvent } from "ol/Object";
import { useElementSize, useFullscreen } from "@vueuse/core";
import { type Unit } from "@/api";
import { gradientOptions } from "@/components/gradient";
import { backgroundOptions } from "@/components/tile-providers";
import { downloadPng } from "@/util/download";
import { getBbox, sleep, waitFor } from "@/util/misc";

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

/** parse geojson features */
const features = computed(() => new GeoJSON().readFeatures(props.geometry));

/** combined lat/long coords */
const center = computed(() => [props.long, props.lat]);

/** background tile url template */
const backgroundUrl = computed(
  () =>
    backgroundOptions.find((option) => option.id === props.background)
      ?.template ?? "",
);

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

/** change cursor to indicate click-ability */
watchEffect(() => {
  const map = mapRef.value?.map;
  /** https://stackoverflow.com/questions/26022029/how-to-change-the-cursor-on-hover-in-openlayers-3 */
  map?.on("pointermove", ({ originalEvent }) => {
    const hit = map.hasFeatureAtPixel(map.getEventPixel(originalEvent));
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
    style: {
      transform: `scale(${scale})`,
      transformOrigin: "top left",
    },
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
