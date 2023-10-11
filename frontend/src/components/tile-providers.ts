import * as L from "leaflet";
import type { Option } from "@/components/AppSelect.vue";
import "leaflet-providers";

/** some pretty base layer tile providers */
/** from https://leaflet-extras.github.io/leaflet-providers/preview/ */
export const baseOptions = [
  "Stadia.OSMBright",
  "Stadia.AlidadeSmooth",
  "Stadia.AlidadeSmoothDark",
  "Stadia.StamenTerrainBackground",
  "Stadia.StamenTonerLite",
  "Stadia.StamenToner",
  "Stadia.StamenTerrain",
  "Stadia.Outdoors",
  "Stadia.StamenWatercolor",
  "CartoDB.Voyager",
  "CartoDB.VoyagerNoLabels",
  "CartoDB.VoyagerLabelsUnder",
  "CartoDB.Positron",
  "CartoDB.PositronNoLabels",
  "CartoDB.PositronOnlyLabels",
  "OpenStreetMap.Mapnik",
  "OpenStreetMap.HOT",
  "Esri.WorldTopoMap",
  "Esri.WorldTerrain",
  "Esri.WorldShadedRelief",
  "Esri.WorldPhysical",
  "Esri.WorldImagery",
  "Esri.WorldGrayCanvas",
  "Esri.WorldStreetMap",
  "Esri.DeLorme",
  "USGS.USTopo",
  "USGS.USImagery",
  "USGS.USImageryTopo",
  "OpenTopoMap",
  "NASAGIBS.ViirsEarthAtNight2012",
  "Stadia.StamenTerrainLines",
  "Stadia.StamenTonerLines",
  "Stadia.StamenTonerLabels",
  "Stadia.StamenTerrainLabels",
  "OpenRailwayMap",
].map(nameToOption) satisfies Option[];

/** get selectable option from tile provider name */
function nameToOption(name: string) {
  /** insert spaces before uppercases */
  /** https://stackoverflow.com/a/7599674/2180570 */
  const label = name
    .split(/(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|\./)
    .join(" ");

  const { _url = "", options } = L.tileLayer.provider(name);
  /** get preview image */
  /** reference: */
  /** https://github.com/leaflet-extras/leaflet-providers/blob/e792f47d3d6cb04c3b0b632ffca7dd21b447b0c3/tests/test.js#L21 */
  /** getTileUrl not workable */
  const image = L.Util.template(_url, {
    /** tile number and zoom. see map image preview css to center exactly. */
    x: 0,
    y: 0,
    z: 0,
    /** highest resolution */
    r: "@2x",
    s: options.subdomains?.[0] || "",
    ...options,
  });

  return { id: name, label, image };
}
