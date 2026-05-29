<template>
  <div
    ref="frameElement"
    class="relative transition-all"
    :style="{
      '--zoom': immediateZoom,
      '--label-opacity': geographyOpacity,
    }"
  >
    <div ref="mapElement" v-bind="$attrs" class="size-full" />

    <!-- legends -->
    <template v-if="showLegends">
      <!-- top left legend -->
      <div
        v-if="$slots['top-left-upper'] || $slots['top-left-lower']"
        ref="topLeftLegend"
        class="absolute top-4 left-4 z-90 flex max-h-full max-w-60 flex-col gap-2 overflow-hidden rounded-md bg-white p-4 shadow-md"
      >
        <slot name="top-left-upper" />

        <!-- scale key -->
        <div
          v-if="scale.steps.length"
          class="grid grid-cols-[repeat(var(--cols),1fr)] grid-rows-[--spacing(6)] gap-y-1"
          :style="{ '--cols': scale.steps.length }"
        >
          <div
            v-for="(step, index) of scale.steps"
            :key="index"
            v-tooltip="step.tooltip"
            class="relative size-full after:absolute after:inset-0 after:[background-image:var(--image)] after:opacity-50 after:content-['']"
            tabindex="0"
            :style="{
              backgroundColor: step.color,
              '--image': step.color === noDataColor ? `url(${hatch})` : 'none',
            }"
          />
          <div
            v-for="(step, index) of scale.steps"
            :key="index"
            class="px-1 text-center wrap-break-word"
          >
            {{ step.label }}
          </div>
        </div>

        <slot name="top-left-lower" />
      </div>

      <!-- top right legend -->
      <div
        v-if="$slots['top-right']"
        ref="topRightLegend"
        class="absolute top-4 right-4 z-90 flex max-h-full max-w-60 flex-col gap-2 overflow-hidden rounded-md bg-white p-4 shadow-md"
      >
        <slot name="top-right" />
      </div>

      <!-- bottom right legend -->
      <div
        v-if="$slots['bottom-right'] || !isEmpty(symbols)"
        ref="bottomRightLegend"
        class="absolute right-4 bottom-4 z-90 flex max-h-full max-w-60 flex-col gap-2 overflow-hidden rounded-md bg-white p-4 shadow-md"
      >
        <slot name="bottom-right" />

        <!-- symbol key -->
        <div
          v-if="!isEmpty(symbols)"
          class="grid grid-cols-[auto_auto] items-center gap-4"
        >
          <template v-for="(symbol, label) of symbols" :key="label">
            <template v-if="symbol">
              <div v-html="symbol.html" />
              <div class="text-sm">{{ label }}</div>
            </template>
          </template>
        </div>
      </div>

      <!-- bottom left legend -->
      <div
        v-if="$slots['bottom-left']"
        ref="bottomLeftLegend"
        class="absolute bottom-4 left-4 z-90 flex max-h-full max-w-60 flex-col gap-2 overflow-hidden rounded-md bg-white p-4 shadow-md"
      >
        <slot name="bottom-left" />
      </div>
    </template>

    <!-- geography labels -->
    <div
      v-for="(feature, index) of geographyFeaturesWLabels"
      :key="index"
      ref="geographyLabelElements"
      class="flex flex-col items-center gap-1 rounded-md text-center text-[calc(var(--zoom)*2px)] text-white select-none text-stroke-1.5 text-stroke-black [:has(>&)]:pointer-events-none"
      :style="{ opacity: geographyOpacity }"
    >
      {{ feature.get("label") }}
    </div>

    <!-- feature popup -->
    <div
      v-if="$slots['popup'] && selectedFeature"
      ref="popupElement"
      v-stop
      class="relative z-100! flex max-h-full w-100 max-w-max translate-y-[calc(--spacing(2)*-1.414)] flex-col gap-2 rounded-md bg-white p-4 shadow-md after:absolute after:top-full after:left-1/2 after:size-2 after:-translate-1/2 after:rotate-45 after:bg-white after:shadow-md after:content-[''] after:[clip-path:polygon(200%_-100%,200%_200%,-100%_200%)]"
    >
      <slot
        name="popup"
        :feature="selectedFeature.getProperties() as FeatureProperties"
      />
    </div>

    <div
      class="absolute bottom-0 left-0 bg-white/75 p-0.5 text-xs text-balance"
      v-html="attribution"
    />
  </div>
</template>

<script lang="ts">
/** "no data" color */
const noDataColor = "#a0a0a0";

/** "no data scale entry */
export const noDataEntry = {
  value: "",
  label: "ND",
  color: noDataColor,
  tooltip: "No data or suppressed value",
} as const;

type Properties = {
  [key: PropertyKey]: unknown;
};
</script>

<script
  setup
  lang="ts"
  generic="
    GeographyProperties extends Properties & {
      value?: number | string;
      center?: [number, number];
    },
    LocationProperties extends Properties & {
      symbol?: string;
      translate?: [number, number];
    }
  "
>
import type { Ref } from "vue";
import type { FeatureCollection, Geometry } from "geojson";
import type { FeatureLike } from "ol/Feature";
import type { Geometry as OLGeometry } from "ol/geom";
import type { MarkerType } from "./markers";
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  onUpdated,
  ref,
  useTemplateRef,
  watch,
  watchEffect,
} from "vue";
import { type Unit } from "@/api";
import hatch from "@/assets/hatch.svg?no-inline";
import { backgroundOptions } from "@/components/background";
import { getGradient, gradientOptions } from "@/components/gradient";
import { formatValue, normalizedApply } from "@/util/math";
import { getCssVar, sleep, waitFor } from "@/util/misc";
import { useElementSize } from "@vueuse/core";
import { extent, pairs, range, scaleQuantile, ticks, tickStep } from "d3";
import { debounce, isEmpty, upperFirst } from "lodash";
import { Feature, Map, Overlay, View } from "ol";
import { pointerMove } from "ol/events/condition";
import GeoJSON from "ol/format/GeoJSON";
import { Point } from "ol/geom";
import MouseWheelZoom from "ol/interaction/MouseWheelZoom";
import Select from "ol/interaction/Select";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import { XYZ } from "ol/source";
import VectorSource from "ol/source/Vector";
import { Fill, Icon, Stroke, Style, Text } from "ol/style";
import { getMarkers } from "./markers";

const frameElement = useTemplateRef("frameElement");
const mapElement = useTemplateRef("mapElement");
const popupElement = useTemplateRef("popupElement");
const geographyLabelElements = useTemplateRef("geographyLabelElements");
const topLeftLegend = useTemplateRef("topLeftLegend");
const topRightLegend = useTemplateRef("topRightLegend");
const bottomRightLegend = useTemplateRef("bottomRightLegend");
const bottomLeftLegend = useTemplateRef("bottomLeftLegend");

const theme = getCssVar("--color-theme");

type Props = {
  /** features */
  geography?: FeatureCollection<Geometry, GeographyProperties>;
  locations?: FeatureCollection<Geometry, LocationProperties>[];
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
  geographyOpacity?: number;
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
  /** id of feature to highlight and zoom in on */
  highlight?: string;
};

const {
  geography = { type: "FeatureCollection", features: [] },
  locations = [],
  min,
  max,
  unit,
  lat = 0,
  long = 0,
  zoom = 0,
  showLegends = true,
  backgroundOpacity = 1,
  geographyOpacity = 0.75,
  locationOpacity = 1,
  background = backgroundOptions[0]!.id,
  gradient = gradientOptions[3]!.id,
  flipGradient = false,
  scaleSteps = 5,
  niceSteps = false,
  scalePower = 1,
  scaleValues = [],
  highlight = "",
} = defineProps<Props>();

type Emits = {
  "update:zoom": [Props["zoom"]];
  "update:lat": [Props["lat"]];
  "update:long": [Props["long"]];
};

const emit = defineEmits<Emits>();

type FeatureProperties = LocationProperties & GeographyProperties;

type Slots = {
  "top-left-upper"?: () => unknown;
  "top-left-lower"?: () => unknown;
  "top-right"?: () => unknown;
  "bottom-right"?: () => unknown;
  "bottom-left"?: () => unknown;
  popup?: ({ feature }: { feature: FeatureProperties }) => unknown;
};

defineSlots<Slots>();

/** whether map has any "no data" values */
const noData = computed(() =>
  geography.features.some((feature) => feature.properties.value === undefined),
);

/** scale object */
const scale = computed(() => {
  /** map 0-1 percent to color */
  const gradientFunc = (percent: number) => {
    /** get gradient interpolator function from shorthand id/name */
    const gradientFunc = getGradient(gradient);
    /** reverse */
    if (flipGradient) percent = 1 - percent;
    /** get color */
    return gradientFunc(percent);
  };

  /** scale steps */
  const steps: ((
    | { value: number | string }
    | { lower: number; upper: number }
  ) & { label: string; color: string; tooltip: string })[] = [];

  /** map specific values to specific colors */
  if (scaleValues.length) {
    /** add "no data" entry */
    if (noData.value) steps.push(noDataEntry);

    /** explicit steps */
    steps.push(
      ...scaleValues.map((value, index, array) => {
        const label =
          typeof value === "number"
            ? formatValue(value, unit, true)
            : upperFirst(value);
        return {
          value,
          label,
          color: gradientFunc(index / (array.length - 1)),
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
    /** map continuous values to discrete colors */
    /** (if we have needed and valid values) */
    typeof min === "number" &&
    typeof max === "number" &&
    min !== max
  ) {
    /** scale bands (spaced list of points between min and max) */
    let bands = [min, max];

    /** "nice", approximate number of steps */
    if (niceSteps) {
      bands = ticks(min, max, scaleSteps);

      /** make sure steps always covers/contains range of values (min/max) */
      const step = tickStep(min, max, scaleSteps);
      if (bands.at(0)! > min) bands.unshift(bands.at(0)! - step);
      if (bands.at(-1)! < max) bands.push(bands.at(-1)! + step);
    } else {
      /** exact number of steps */
      bands = range(min, max, (max - min) / scaleSteps).concat([max]);
    }

    /** make sure enough bands */
    if (bands.length < 3) bands = [min, (min + max) / 2, max];

    /** range of bands */
    const [lower = 0, upper = 1] = extent(bands);

    /** apply power */
    bands = bands.map((value) =>
      normalizedApply(value, lower, upper, (value) =>
        Math.pow(value, scalePower),
      ),
    );

    /** derive props for each step between points */
    steps.push(
      ...pairs(bands).map(([lower, upper], index, array) => ({
        lower,
        upper,
        label:
          /** only add first and last labels */
          index === 0
            ? formatValue(min, unit, true)
            : index === array.length - 1
              ? formatValue(max, unit, true)
              : "",
        color: gradientFunc(index / (array.length - 1)),
        tooltip: `${formatValue(lower, unit)} &ndash; ${formatValue(upper, unit)}`,
      })),
    );

    /** get colors (excluding "no data" entry) for scale range */
    const colors = steps.map((step) => step.color);

    /** add "no data" entry to start of list */
    if (noData.value) steps.unshift(noDataEntry);

    /** scale interpolator */
    const getColor = (value?: number | string) =>
      typeof value === "number"
        ? scaleQuantile<string>().domain(bands).range(colors)(value)
        : noDataColor;

    return { steps, getColor };
  } else {
    /** last resort fallback */
    return { steps: [noDataEntry], getColor: () => noDataColor };
  }
});

/** map object */
const map = new Map({ controls: [] });

/** update map root element */
watchEffect(() => map.setTarget(mapElement.value ?? undefined));

/** mercator https://epsg.io/3857 */
const xy = "EPSG:3857";
/** world geodetic system https://epsg.io/4326 */
const longLat = "EPSG:4326";

/** transform point coordinates */
const xyToLongLat = (x = 0, y = 0) => {
  const [long = 0, lat = 0] = new Point([x, y])
    .transform(xy, longLat)
    .getCoordinates();
  return [long, lat];
};

/** transform point coordinates */
const longLatToXy = (long = 0, lat = 0) => {
  const [x = 0, y = 0] = new Point([long, lat])
    .transform(longLat, xy)
    .getCoordinates();
  return [x, y];
};

/** view object */
const view = new View({
  projection: xy,
  smoothExtentConstraint: false,
  smoothResolutionConstraint: false,
});

/** remove default zoom animation */
const mouseZoom = new MouseWheelZoom({ duration: 0, timeout: 0 });
map.addInteraction(mouseZoom);

/** add view to map */
watchEffect(() => map.setView(view));

/** update view center */
watchEffect(() => view.setCenter(longLatToXy(long, lat)));
/** update view zoom */
watchEffect(() => view.setZoom(zoom));

/** on view pan */
view.on("change:center", () => {
  const center = view.getCenter();
  if (!center) return;
  const [long, lat] = xyToLongLat(center[0], center[1]);
  emit("update:long", long);
  emit("update:lat", lat);
});

/** on view zoom */
view.on("change:resolution", () => {
  const zoom = view.getZoom();
  if (!zoom) return;
  emit("update:zoom", zoom);
});

/** on immediate view zoom */
const immediateZoom = ref(view.getZoom());
view.on("change:resolution", () => (immediateZoom.value = view.getZoom()));

/** background source object */
const backgroundSource = new XYZ({
  projection: xy,
  crossOrigin: "anonymous",
});
/** background layer object */
const backgroundLayer = new TileLayer({ source: backgroundSource });

/** attribution html */
const attribution = ref("");

/** update background layer url template */
watchEffect(() => {
  /** clear tile cache at all zoom levels */
  backgroundLayer.clearRenderer();
  /** look up full option details */
  const option = backgroundOptions.find((option) => option.id === background);
  if (!option) return;
  backgroundSource.setUrl(option.template ?? "");
  attribution.value = option.attribution;
});

/** update background layer opacity */
watchEffect(() => backgroundLayer.setOpacity(backgroundOpacity));

/** geography source object */
const geographySource = new VectorSource();
/** geography layer object */
const geographyLayer = new VectorLayer({ source: geographySource });

/** geojson parser */
const geojson = new GeoJSON({
  /** source projection */
  dataProjection: longLat,
  /** target projection */
  featureProjection: xy,
});

/** parse geography features */
const geographyFeatures = computed(
  () =>
    geojson.readFeatures(geography) as Feature<
      OLGeometry,
      GeographyProperties
    >[],
);

/** update geography layer source */
watchEffect(() => {
  geographySource.clear();
  geographySource.addFeatures(geographyFeatures.value);
});

/** update geography styles */
watchEffect((onCleanup) => {
  /** get reactive values in root of watch so they can be auto-tracked */
  const getColor = scale.value.getColor;
  const _highlight = highlight;

  /** generate styles per feature */
  const style =
    (hover = false) =>
    (feature: FeatureLike) => {
      const color =
        feature.getId() === _highlight ? theme : getColor(feature.get("value"));
      return new Style({
        stroke: new Stroke({ color: "black", width: hover ? 4 : 1 }),
        fill: new Fill({
          color: color === noDataColor ? { color, src: hatch } : color,
        }),
        zIndex: hover ? 1 : 0,
      });
    };

  /** base styles */
  geographyLayer.setStyle(style());

  /** hover styles */
  const hover = new Select({
    condition: pointerMove,
    style: style(true),
    /** don't count other layers, e.g. labels, in hover */
    layers: [geographyLayer],
  });

  /** add interaction to map */
  map.addInteraction(hover);
  /** remove interaction from map (avoid memory leak) */
  onCleanup(() => map.removeInteraction(hover));
});

/** update geography layer opacity */
watchEffect(() => geographyLayer.setOpacity(geographyOpacity));

/** symbols (icon + label) associated with each location */
const symbols = computed(() =>
  getMarkers(
    locations
      .map((location) => {
        const feature = location.features[0];
        if (!feature) return;
        const symbol = feature.properties.symbol;
        if (typeof symbol !== "string") return;
        return [symbol, feature.geometry.type] as [string, MarkerType];
      })
      .filter((entry) => !!entry),
  ),
);

/** parse location features */
const locationFeatures = computed(() =>
  locations.map((location) => {
    /** parse geojson */
    const features = geojson.readFeatures(location) as Feature<
      OLGeometry,
      LocationProperties
    >[];

    for (const feature of features) {
      const symbol = symbols.value[feature.get("symbol")];
      if (!symbol) continue;

      /** add extra props */
      for (const [key, value] of Object.entries(symbol))
        feature.set(key, value);

      const { src, width, height } = symbol;

      /** define icon object here instead of on more frequent style update */
      feature.set("icon", new Icon({ src, width, height }));
      feature.set(
        "iconHover",
        new Icon({ src, width, height, color: "black" }),
      );
    }

    return features;
  }),
);

/** locations source object */
const locationsSource = new VectorSource();
/** locations layer object */
const locationsLayer = new VectorLayer({ source: locationsSource });

/** update locations layer source */
watchEffect(() => {
  locationsSource.clear();
  for (const features of locationFeatures.value)
    locationsSource.addFeatures(features);
});

/** update location styles */
watchEffect((onCleanup) => {
  /** generate styles per feature */
  const style =
    (hover = false) =>
    (feature: FeatureLike) => {
      const { color, icon, iconHover, label, dash, displacement } =
        feature.getProperties();

      const text = new Text({
        text: label === undefined || label === null ? undefined : String(label),
        font: "12px Roboto",
        fill: new Fill({ color: "white" }),
        stroke: new Stroke({ color: "black", width: 2 }),
        offsetY: 1,
      });

      /** adjust icon/text/etc offset */
      if (displacement) {
        icon.setDisplacement(displacement);
        iconHover.setDisplacement(displacement);
        text.setOffsetX(displacement[0]);
        text.setOffsetY(-displacement[1] + 1);
      }

      return new Style({
        text,
        fill: new Fill({ color: hover ? color + "80" : color + "20" }),
        stroke: new Stroke({ color, width: hover ? 6 : 2, lineDash: dash }),
        image: hover ? iconHover : icon,
        zIndex: hover ? 2 : 1,
      });
    };

  /** base styles */
  locationsLayer.setStyle(style());

  /** hover styles */
  const hover = new Select({
    condition: pointerMove,
    style: style(true),
    /** don't count other layers, e.g. labels, in hover */
    layers: [locationsLayer],
  });

  /** add interaction to map */
  map.addInteraction(hover);
  /** remove interaction from map (avoid memory leak) */
  onCleanup(() => map.removeInteraction(hover));
});

/** update locations layer opacity */
watchEffect(() => locationsLayer.setOpacity(locationOpacity));

/** geography features that have a position for a label */
const geographyFeaturesWLabels = computed(() =>
  geographyFeatures.value.filter((feature) => feature.get("center")),
);

/** update geography feature labels */
watchEffect(async (onCleanup) => {
  /** get reactive values before async so they can be auto-tracked */
  /** https://github.com/vuejs/core/issues/2093 */
  const elements = geographyLabelElements.value ?? [];
  const features = geographyFeaturesWLabels.value;

  /** https://stackoverflow.com/questions/79031309/usetemplateref-is-not-reactive-for-arrays */
  await nextTick();

  for (let index = 0; index < elements.length; index++) {
    /** element */
    const element = elements[index]!;
    if (!element) continue;
    /** feature associated with element */
    const feature = features[index];
    if (!feature) continue;
    const [long, lat] = feature.get("center") ?? [];
    /** don't create overlay if cent position not defined */
    if (!long || !lat) continue;
    /** overlay object */
    const overlay = new Overlay({
      element,
      position: longLatToXy(long, lat),
      positioning: "center-center",
      className: "pointer-events-none!",
    });
    map.addOverlay(overlay);
    onCleanup(() => {
      map.removeOverlay(overlay);
      overlay.dispose();
    });
  }
});

/** current selected feature */
const selectedFeature = ref<Feature<OLGeometry>>();

/** reset selected feature when data changes to avoid showing wrong popup info */
watch(
  [() => geography, () => locations],
  () => (selectedFeature.value = undefined),
  { deep: true },
);

/** select feature */
map.on("click", ({ pixel }) => {
  /** do like this instead of select to avoid double click debounce */

  /** reset selected */
  selectedFeature.value = undefined;

  /** https://stackoverflow.com/a/50415743/2180570 */
  map.forEachFeatureAtPixel(pixel, (feature, layer) => {
    if (
      /** select first */
      !selectedFeature.value &&
      feature instanceof Feature &&
      /** don't allow selection of e.g. geography labels */
      (layer === geographyLayer || layer === locationsLayer)
    ) {
      /** set selected */
      selectedFeature.value = feature;
    }
  });
});

/** popup object */
const popup = new Overlay({
  stopEvent: false,
  positioning: "bottom-center",
});

/** add popup to map */
map.addOverlay(popup);

/** update popup element */
watchEffect(() => {
  if (popupElement.value) popup.setElement(popupElement.value);
});

/** update popup position */
watchEffect(async () => {
  if (!selectedFeature.value) return;

  /** get bounds of feature */
  const extent = selectedFeature.value.getGeometry()?.getExtent();
  if (!extent) return;

  /** position popup */
  const [left = 0, bottom = 0, right = 0, top = 0] = extent;
  popup.setPosition([left + (right - left) * 0.5, top + (bottom - top) * 0.25]);

  /** wait for popup to render */
  await nextTick();

  /** move view if needed */
  popup.panIntoView({ animation: { duration: 0 } });
});

/** change cursor to indicate click-ability */
map.on("pointermove", ({ pixel }) => {
  /**
   * select canvas element specifically so not everything within map element
   * (e.g. popups) have their cursor set
   */
  const canvas = mapElement.value?.querySelector("canvas");
  if (!canvas) return;
  /** https://stackoverflow.com/questions/26022029/how-to-change-the-cursor-on-hover-in-openlayers-3 */
  canvas.style.cursor = map.hasFeatureAtPixel(pixel) ? "pointer" : "";
});

/** add layers to map */
watchEffect(() =>
  map.setLayers([backgroundLayer, geographyLayer, locationsLayer]),
);

/** preview image of canvas */
const thumbnail = ref("");

/** make thumbnail blob from canvas */
const generateThumbnail = debounce(async () => {
  console.log("generate");
  URL.revokeObjectURL(thumbnail.value);
  const canvas = mapElement.value?.querySelector("canvas");
  if (!canvas) return;
  const blob = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, "image/jpeg", 0.1);
  });
  if (!blob) return (thumbnail.value = "");
  const src = URL.createObjectURL(blob);
  thumbnail.value = src;
}, 500);

/** generate thumbnail on any map update */
onMounted(generateThumbnail);
onUpdated(generateThumbnail);
/** cancel any pending debounce */
onUnmounted(generateThumbnail.cancel);
/** clean up thumbnail object url */
onUnmounted(() => URL.revokeObjectURL(thumbnail.value));

/** programmatic zoom in */
const zoomIn = () => view.setZoom((view.getZoom() ?? 0) + 1);

/** programmatic zoom out */
const zoomOut = () => view.setZoom((view.getZoom() ?? 2) - 1);

/** map client size */
const { width: mapWidth, height: mapHeight } = useElementSize(frameElement);

/** fit view to geography layer content or highlighted feature */
const fit = async () => {
  /** wait for view to be attached to map */
  await waitFor(() => !!map.getView());
  /** wait for legends to render */
  await sleep();

  /** get bounding box */
  const extent = highlight
    ? /** highlighted feature */
      geographyFeatures.value
        /** lookup feature by id */
        .find((feature) => feature.getId() === highlight)
        ?.getGeometry()
        ?.getExtent()
    : /** geography layer */
      geographySource.getExtent();

  /** check if valid extent (can be infinities if no features) */
  if (!extent || extent.some((value) => !Number.isFinite(value))) return;

  /** default fit padding */
  const padding = { top: 0, left: 0, bottom: 0, right: 0 };

  /** make room for legends */
  if (showLegends) {
    /** increase padding based on corner legend panel dimensions */
    const padCorner = (
      v: "top" | "bottom",
      h: "left" | "right",
      legend: Ref<HTMLElement | null>,
    ) => {
      /** get client size of legend elements */
      const { width, height } =
        legend.value?.getBoundingClientRect() ?? new DOMRect(0, 0, 1, 1);
      if (mapWidth.value > mapHeight.value)
        /** if map landscape aspect ratio */
        padding[h] = Math.max(width, padding[h]);
      else
        /** if map portrait aspect ratio */
        padding[v] = Math.max(height, padding[v]);
    };
    /** pad each corner */
    padCorner("top", "left", topLeftLegend);
    padCorner("top", "right", topRightLegend);
    padCorner("bottom", "left", bottomLeftLegend);
    padCorner("bottom", "right", bottomRightLegend);
  }

  const { top, right, bottom, left } = padding;
  /** fit view, add some extra padding */
  view.fit(extent, {
    padding: [top, right, bottom, left].map((v) => v + 20),
  });

  if (highlight)
    /** zoom out a bit to give context of surroundings */
    view.adjustZoom(-1);
};

onMounted(async () => {
  /** if no initial view provided, fit to content */
  /** wait for features to be loaded, rendered/parsed */
  await waitFor(() => geographySource.getFeatures().length);
  /** preserve existing view */
  if (!zoom || !lat || !long)
    /** fit view to content */
    fit();
});

/** get geojson data */
const getGeo = (): FeatureCollection => ({
  type: "FeatureCollection",
  features: [
    ...geojson.writeFeaturesObject(geographySource.getFeatures()).features,
    ...geojson.writeFeaturesObject(locationsSource.getFeatures()).features,
  ],
});

/** allow control from parent */
defineExpose({ zoomIn, zoomOut, fit, getGeo, thumbnail });

/** clean up objects */
onUnmounted(() => {
  map.dispose();
  view.dispose();
  backgroundLayer.dispose();
  backgroundSource.dispose();
  geographyLayer.dispose();
  geographySource.dispose();
  locationsLayer.dispose();
  locationsSource.dispose();
  popup.dispose();
});
</script>

<style>
.ol-overlaycontainer {
  z-index: 100 !important;
}
</style>
