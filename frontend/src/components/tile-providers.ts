import { startCase } from "lodash";
import providers from "@/assets/tile-providers.json";
import type { Option } from "@/components/AppSelect.vue";

/**
 * https://leaflet-extras.github.io/leaflet-providers/preview/
 * https://github.com/leaflet-extras/leaflet-providers/issues/457
 * https://raw.githubusercontent.com/geopandas/xyzservices/refs/heads/main/provider_sources/leaflet-providers-parsed.json
 */

/** some pretty background layer tile providers */
export const backgroundOptions = (
  [
    providers.Stadia.AlidadeSmooth,
    providers.Stadia.AlidadeSmoothDark,
    providers.Stadia.OSMBright,
    providers.Stadia.StamenTerrainBackground,
    providers.Stadia.StamenTonerLite,
    providers.Stadia.StamenToner,
    providers.Stadia.StamenTerrain,
    providers.Stadia.Outdoors,
    providers.Stadia.StamenWatercolor,
    providers.CartoDB.Voyager,
    providers.CartoDB.VoyagerNoLabels,
    providers.CartoDB.VoyagerLabelsUnder,
    providers.CartoDB.Positron,
    providers.CartoDB.PositronNoLabels,
    providers.CartoDB.PositronOnlyLabels,
    providers.OpenStreetMap.Mapnik,
    providers.OpenStreetMap.HOT,
    providers.Esri.WorldTopoMap,
    providers.Esri.WorldTerrain,
    providers.Esri.WorldShadedRelief,
    providers.Esri.WorldPhysical,
    providers.Esri.WorldImagery,
    providers.Esri.WorldGrayCanvas,
    providers.Esri.WorldStreetMap,
    providers.USGS.USTopo,
    providers.USGS.USImagery,
    providers.USGS.USImageryTopo,
    providers.OpenTopoMap,
    providers.NASAGIBS.ViirsEarthAtNight2012,
    providers.Stadia.StamenTerrainLines,
    providers.Stadia.StamenTonerLines,
    providers.Stadia.StamenTonerLabels,
    providers.Stadia.StamenTerrainLabels,
    providers.OpenRailwayMap,
  ] as const
).map((provider) => {
  /** make nice label */
  const label = startCase(provider.name);

  /** get xyz url template */
  let template = provider.url.replace("{r}", "@2x").replace(
    "{s}",
    "subdomains" in provider
      ? provider.subdomains[0]!
      : /**
         * fallback with typical sub-domain, e.g.
         * https://wiki.openstreetmap.org/wiki/Raster_tile_providers
         */
        "a",
  );
  /** replace all template vars */
  for (const [key, value] of Object.entries(provider))
    template = template.replace(`{${key}}`, String(value));

  /** get preview image */
  const image = template
    /** tile number and zoom. see map image preview css to center exactly. */
    .replace("{x}", "0")
    .replace("{y}", "0")
    .replace("{z}", "0");

  return { id: provider.name, label, image, template } satisfies Option;
});
