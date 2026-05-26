import type { Feature } from "@/api/feature";
import type { Geographies, Geography } from "@/api/geography";
import type { Statistic, Statistics } from "@/api/statistic";
import type { Geometry } from "geojson";
import type { Point } from "./";
import { http, HttpResponse, passthrough } from "msw";
import { setupWorker } from "msw/browser";
import { api } from "./";

/** temporary interface between real api structure and desired api structure */

const handlers = [
  http.get("/geography", async () => {
    const url = new URL(`${api}/stats/measures`);

    const actual: _StatsMeasures = await (await fetch(url)).json();

    const desired: Geographies = Object.fromEntries(
      Object.keys(actual).map((key) => [key, {}]),
    );

    return HttpResponse.json(desired);
  }),

  http.get("/geography/:level", async ({ params }) => {
    const path =
      { county: "counties", tract: "tracts", healthregion: "healthregions" }[
        params.level as string
      ] ?? "";
    const url = new URL(`${api}/${path}`);

    const actual: _Level = await (await fetch(url)).json();

    const desired: Geography = Object.fromEntries(
      actual.map((feature) => {
        const id =
          feature.us_fips ?? feature.fips ?? String(feature.hs_region) ?? "";
        const center = [feature.cent_lat, feature.cent_long] as Point;
        return [
          id,
          {
            geometry: JSON.parse(feature.wkb_geometry ?? "{}") as Geometry,
            center,
            description: feature.counties,
          },
        ];
      }),
    );

    return HttpResponse.json(desired);
  }),

  http.get("/feature/:feature", async ({ params }) => {
    const url = new URL(`${api}/stats/by-county/${params.feature as string}`);

    const actual: _StatsByCounty = await (await fetch(url)).json();

    const desired: Feature = actual;

    return HttpResponse.json(desired);
  }),

  http.get("/statistic", async () => {
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

  http.get("/statistic/:statistic", async ({ request, params }) => {
    const [category = "", measure = ""] =
      (params.statistic as string).split(";") ?? [];
    const level = new URL(request.url).searchParams.get("level") ?? "";
    const factors = new URL(request.url).searchParams.get("factors") ?? "";
    const url = new URL(`${api}/stats/${level}/${category}/fips-value?`);
    url.searchParams.set("measure", measure);
    url.searchParams.set("factors", factors);

    const actual: _StatsFipsValue = await (await fetch(url)).json();

    const desired: Statistic = actual;

    return HttpResponse.json(desired);
  }),

  /** leave all other requests untouched */
  http.get("*", passthrough),
  http.post("*", passthrough),
];

/** start mocking */
export const mock = () => setupWorker(...handlers);

/** /stats/measures */
type _StatsMeasures = {
  [key: string]: {
    label: string;
    categories: {
      [key: string]: {
        label: string;
        measures: {
          [key: string]: {
            label: string;
            factors?: {
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

/** /${level} */
type _Level = {
  /** counties */
  wkb_geometry?: string;
  us_fips?: string;
  cnty_fips?: string;
  num_fips?: number;
  county?: string;
  full?: string;
  label?: string;
  cent_lat?: number;
  cent_long?: number;
  ogc_fid?: number;
  objectid?: number;

  /** tracts */
  // wkb_geometry?: string;
  fips?: string;
  // ogc_fid?: number;
  // objectid?: number;

  /** healthregions */
  // wkb_geometry?: string;
  hs_region?: string;
  counties?: string;
  // ogc_fid?: number;
  // objectid?: number;
}[];

/** /stats/by-county/${county} */
type _StatsByCounty = {
  FIPS: string;
  name: string;
  categories: {
    [key: string]: {
      label: string;
      measures: {
        [key: string]: {
          label: string;
          value: number | string;
          state_value?: number | string;
          aac?: number | string;
          state_aac?: number | string;
          unit: Unit;
          order?: string[];
        };
      };
    };
  };
};

/** value type/format */
type Unit =
  | "count"
  | "percent"
  | "rate"
  | "dollar_amount"
  | "rank"
  | "least_most"
  | "ordinal"
  | null;

/** /stats/${level}/${category}/fips-value */
type _StatsFipsValue = {
  /** range of values for specified measure */
  max: number | string;
  min: number | string;
  /** "global" value */
  state?: number | string;
  state_source?: string;
  /** map of feature id to measure value */
  values: {
    [key: string]: {
      value?: number | string | null;
      aac?: number | string | null;
    };
  };
  /** unit info */
  unit: Unit;
  order?: string[];
  /** where data came from */
  source?: string;
  source_url?: string;
};
