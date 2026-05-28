import type { FeatureCollection, Geometry } from "geojson";
import type {
  Feature,
  Level,
  Levels,
  Location,
  Locations,
  Point,
  Statistic,
  Statistics,
} from "./";
import sourceDetails from "@/api/data/source-details.json";
import { mapValues } from "lodash";
import { http, HttpResponse, passthrough } from "msw";
import { setupWorker } from "msw/browser";
import { api } from "./";

/** temporary interface between real api structure and desired api structure */

const handlers = [
  http.get("*/level", async () => {
    const url = new URL(`${api}/stats/measures`);

    const actual: _StatsMeasures = await (await fetch(url)).json();

    const desired: Levels = Object.fromEntries(
      Object.keys(actual).map((key) => [key, {}]),
    );

    return HttpResponse.json(desired);
  }),

  http.get("*/level/:level", async ({ params }) => {
    const level = params.level as string;
    const path =
      { county: "counties", tract: "tracts", healthregion: "healthregions" }[
        level
      ] ?? "";
    const url = new URL(`${api}/${path}`);

    const actual: _Level = await (await fetch(url)).json();

    const desired: Level = {
      type: "FeatureCollection",
      features: actual.map((feature) => {
        return {
          id:
            feature.us_fips ?? feature.fips ?? String(feature.hs_region) ?? "",
          type: "Feature",
          geometry: JSON.parse(feature.wkb_geometry ?? "{}") as Geometry,
          properties: {
            center:
              feature.cent_lat !== undefined && feature.cent_long !== undefined
                ? ([feature.cent_long, feature.cent_lat] as Point)
                : undefined,
            description: feature.counties,
          },
        };
      }),
    };

    return HttpResponse.json(desired);
  }),

  http.get("*/statistic", async () => {
    const url = new URL(`${api}/stats/measures`);

    const actual: _StatsMeasures = await (await fetch(url)).json();

    const desired: Statistics = {};

    for (const [level, { categories }] of Object.entries(actual))
      for (const [category, { measures }] of Object.entries(categories))
        for (const [measure, { factors = {} }] of Object.entries(measures)) {
          const id = [category, measure].join(";");
          desired[id] ??= { levels: [], factors: {} };
          if (!desired[id].levels.includes(level))
            desired[id].levels.push(level);
          for (const [factor, { default: _default, values }] of Object.entries(
            factors,
          )) {
            /** always put default first */
            desired[id].factors[factor] ??= [_default];
            for (const value of Object.keys(values))
              if (!desired[id].factors[factor].includes(value))
                desired[id].factors[factor].push(value);
          }
        }

    return HttpResponse.json(desired);
  }),

  http.get("*/statistic/:statistic", async ({ request, params }) => {
    const statistic = params.statistic as string;
    const [category = "", measure = ""] = statistic.split(";") ?? [];
    const level = new URL(request.url).searchParams.get("level") ?? "";
    const factors = new URL(request.url).searchParams.get("factors") ?? "";
    const url = new URL(`${api}/stats/${level}/${category}/fips-value?`);
    url.searchParams.set("measure", measure);
    url.searchParams.set("factors", factors);

    const actual: _StatsFipsValue = await (await fetch(url)).json();

    const desired: Statistic = {
      values: mapValues(actual.values, ({ value, aac }) => ({
        value: value ?? 0,
        aac: aac ?? 0,
      })),
      min: actual.min ?? undefined,
      max: actual.max ?? undefined,
      unit: actual.unit ?? "count",
      order: actual.order ?? undefined,
      source:
        Object.keys(sourceDetails).find(
          (key) => !!actual.source?.match(new RegExp(key, "i")),
        ) ?? undefined,
      state: actual.state ?? undefined,
      state_source:
        Object.keys(sourceDetails).find(
          (key) => !!actual.source?.match(new RegExp(key, "i")),
        ) ?? undefined,
    };

    return HttpResponse.json(desired);
  }),

  http.get("*/location", async () => {
    const url = new URL(`${api}/locations`);

    const actual: _Locations = await (await fetch(url)).json();

    const desired: Locations = Object.fromEntries(
      Object.values(actual)
        .flatMap((group) => Object.values(group))
        .map((id) => [id, {}]),
    );

    return HttpResponse.json(desired);
  }),

  http.get("*/location/:location", async ({ params }) => {
    const location = params.location as string;
    const url = new URL(`${api}/locations/${location}`);

    const actual: _Location = await (await fetch(url)).json();

    const desired: Location = {
      type: "FeatureCollection",
      features: actual.geometry_json.features.map((feature) => ({
        ...feature,
        properties: {
          ...feature.properties,
          /** add name */
          name:
            feature.properties.name ??
            String(feature.properties.district) ??
            "",
        },
      })),
    };

    return HttpResponse.json(desired);
  }),

  http.get("*/feature/:feature", async ({ params }) => {
    const feature = params.feature as string;
    const url = new URL(`${api}/stats/by-county/${feature}`);

    const actual: _StatsByCounty = await (await fetch(url)).json();

    const desired: Feature = Object.fromEntries(
      Object.entries(actual.categories).flatMap(([category, { measures }]) =>
        Object.entries(measures).map(([measure, value]) => [
          `${category};${measure}`,
          {
            value: value.value ?? 0,
            aac: value.aac ?? 0,
            unit: value.unit ?? "count",
            state_value: value.state_value ?? 0,
            state_aac: value.state_aac ?? 0,
            order: value.order ?? [],
          },
        ]),
      ),
    );

    return HttpResponse.json(desired);
  }),

  /** leave all other requests untouched */
  http.get("**", passthrough),
  http.post("*", passthrough),
];

/** start mocking */
export const mock = () => setupWorker(...handlers).start();

type _StatsMeasures = {
  [key: string]: {
    label: string;
    categories: {
      [key: string]: {
        label: string;
        measures: {
          [key: string]: {
            label: string;
            factors: {
              [key: string]: {
                label: string;
                default: string;
                values: { [key: string]: string };
              };
            };
          };
        };
      };
    };
  };
};

type _Level = Partial<{
  /** counties */
  wkb_geometry: string;
  us_fips: string;
  cnty_fips: string;
  num_fips: number;
  county: string;
  full: string;
  label: string;
  cent_lat: number;
  cent_long: number;
  ogc_fid: number;
  objectid: number;

  /** tracts */
  // wkb_geometry: string;
  fips: string;
  // ogc_fid: number;
  // objectid: number;

  /** healthregions */
  // wkb_geometry: string;
  hs_region: string;
  counties: string;
  // ogc_fid: number;
  // objectid: number;
}>[];

type _StatsByCounty = {
  FIPS: string;
  name: string;
  categories: {
    [key: string]: {
      label: string;
      measures: {
        [key: string]: Partial<{
          label: string;
          value: Value;
          aac: Value;
          unit: Unit;
          state_value: Value;
          state_aac: Value;
          order: string[];
        }>;
      };
    };
  };
};

type Unit =
  | "count"
  | "percent"
  | "rate"
  | "dollar_amount"
  | "rank"
  | "least_most"
  | "ordinal";

type Value = number | string | null | undefined;

type _StatsFipsValue = Partial<{
  values: {
    [key: string]: Partial<{
      value: Value;
      aac: Value;
    }>;
  };
  min: Value;
  max: Value;
  unit: Unit;
  order: string[];
  source: string;
  source_url: string;
  state: Value;
  state_source: string;
}>;

type _Locations = {
  [key: string]: { [key: string]: string };
};

type _Location = {
  id: string;
  name: string;
  category_id: string;
  geometry_json: FeatureCollection<
    Geometry,
    Partial<{
      name: string;
      org: string;
      link: string;
      address: string;
      phone: string;
      notes: string;
      email: string;
      district: number;
      zip_code: string;
      area_type: string;
      representative: string;
      party: string;
      fips: string;
      zip: string;
      count: number;
    }>
  >;
};
