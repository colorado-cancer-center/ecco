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
        <Sources.OlSourceOsm />
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
              <Styles.OlStyleFill :color="noDataColor" />
            </Styles.OlStyle>
          </Map.OlFeature>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

      <Interactions.OlInteractionSelect :condition="pointerMove">
        <Styles.OlStyle>
          <Styles.OlStyleFill color="black" />
        </Styles.OlStyle>
      </Interactions.OlInteractionSelect>
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
import { computed, ref, watchEffect } from "vue";
import { Interactions, Layers, Map, Sources, Styles } from "vue3-openlayers";
import type { FeatureCollection } from "geojson";
import { pointerMove } from "ol/events/condition";
import GeoJSON from "ol/format/GeoJSON";
import type { ObjectEvent } from "ol/Object";
import { type Unit } from "@/api";
import { gradientOptions } from "@/components/gradient";
import { baseOptions } from "@/components/tile-providers";

/** element refs */
const scrollElement = ref<HTMLDivElement>();
const mapRef = ref<InstanceType<typeof Map.OlMap>>();
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

/** parse geojson features */
const features = computed(() => new GeoJSON().readFeatures(props.geometry));

function zoomIn() {
  viewRef.value?.adjustZoom(1);
}

function zoomOut() {
  viewRef.value?.adjustZoom(-1);
}

function fit() {
  if (!viewRef.value || !geometryRef.value) return;
  const extent = geometryRef.value.source.getExtent();
  if (extent) viewRef.value.fit(extent);
}

/** allow control from parent */
defineExpose({
  zoomIn,
  zoomOut,
  fit,
  download: () => null,
  fullscreen: () => null,
  selectFeature: () => null,
});

function onZoom(event: ObjectEvent) {
  const newZoom = event.target.getZoom();
  if (newZoom) emit("update:zoom", newZoom);
}

const center = computed(() => [props.long, props.lat]);

function onCenter(event: ObjectEvent) {
  const [long, lat] = event.target.getCenter();
  emit("update:lat", lat);
  emit("update:long", long);
}

/** change cursor to indicate clickability */
watchEffect(() => {
  const map = mapRef.value?.map;
  /** https://stackoverflow.com/questions/26022029/how-to-change-the-cursor-on-hover-in-openlayers-3 */
  map?.on("pointermove", function (e) {
    const pixel = map.getEventPixel(e.originalEvent);
    const hit = map.hasFeatureAtPixel(pixel);
    map.getViewport().style.cursor = hit ? "pointer" : "";
  });
});
</script>

<style scoped>
.scroll {
  overflow: auto;
  box-shadow: var(--shadow);
}

.test {
  background: red;
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
