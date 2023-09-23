import * as L from "leaflet";
import type { Option } from "@/components/AppSelect.vue";
import "leaflet-providers";

// some pretty base layer tile providers
// from https://leaflet-extras.github.io/leaflet-providers/preview/
export const baseOptions: Option[] = [
  "Stadia.OSMBright",
  "Stadia.Outdoors",
  "Stadia.AlidadeSmooth",
  "Stadia.AlidadeSmoothDark",
  "Stadia.StamenTerrainBackground",
  "Stadia.StamenTonerLite",
  "Stadia.StamenToner",
  "Stadia.StamenTerrain",
  "Stadia.StamenWatercolor",
  "OpenStreetMap.Mapnik",
  "OpenStreetMap.HOT",
  "OpenTopoMap",
  "Esri.WorldStreetMap",
  "Esri.DeLorme",
  "Esri.WorldTopoMap",
  "Esri.WorldImagery",
  "Esri.WorldTerrain",
  "Esri.WorldShadedRelief",
  "Esri.WorldPhysical",
  "Esri.WorldGrayCanvas",
  "CartoDB.Positron",
  "CartoDB.PositronNoLabels",
  "CartoDB.PositronOnlyLabels",
  "CartoDB.DarkMatter",
  "CartoDB.DarkMatterNoLabels",
  "CartoDB.DarkMatterOnlyLabels",
  "CartoDB.Voyager",
  "CartoDB.VoyagerNoLabels",
  "CartoDB.VoyagerLabelsUnder",
  "NASAGIBS.ViirsEarthAtNight2012",
  "USGS.USTopo",
  "USGS.USImagery",
  "USGS.USImageryTopo",
].map((name) => {
  // https://stackoverflow.com/a/7599674/2180570
  const label = name
    .split(/(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|\./)
    .join(" ");
  // @ts-expect-error no workable type defs for leaflet-providers
  const { _url = "", options } = L.tileLayer.provider(name);
  // get preview image
  const image = L.Util.template(_url, {
    x: 0,
    y: 0,
    z: 1,
    r: "",
    s: options.subdomains[0],
    ...options,
  });
  return { id: name, label, image };
});

// some pretty overlay layer tile Providers/providers
// from https://leaflet-extras.github.io/leaflet-providers/preview/
export const overlayOptions = [
  "OpenRailwayMap",
  "Stadia.StamenTonerLines",
  "Stadia.StamenTonerLabels",
  "Stadia.StamenTerrainLabels",
  "Stadia.StamenTerrainLines",
];

// export function getPreview({ _url, options }: L.TileLayer) {
//   return _url
//     .replace("{variant}", options.variant)
//     .replace("{x}", 0)
//     .replace("{y}", 0)
//     .replace("{z}", 0)
//     .replace("{ext}", options.ext);
// }
