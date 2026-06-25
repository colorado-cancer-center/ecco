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
import { api } from "./";

/** temporary interface between real api structure and desired api structure */

export const _fetch = async (request: Request) => {
  const url = new URL(request.url);
  for (const [pattern, handler] of Object.entries(handlers)) {
    const match = url.pathname.match(new RegExp(pattern));
    if (!match) continue;
    return await handler(
      request,
      ...match.slice(1).map(window.decodeURIComponent),
    );
  }
  throw Error(`No mock handler for ${url}`);
};

const response = async (data: unknown) =>
  new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json" },
  });

const handlers: Record<
  string,
  (request: Request, ...matches: string[]) => Promise<Response>
> = {
  "/level$": async () => {
    const url = new URL(`${api}/stats/measures`);

    const actual: _StatsMeasures = await (await fetch(url)).json();

    const desired: Levels = Object.fromEntries(
      Object.keys(actual).map((key) => [key, {}]),
    );

    return response(desired);
  },

  "/level/(.*)$": async (request, level = "") => {
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

    return response(desired);
  },

  "/statistic$": async () => {
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

    return response(desired);
  },

  "/statistic/(.*)$": async (request, statistic = "") => {
    const [category = "", measure = ""] = statistic.split(";") ?? [];
    const level = new URL(request.url).searchParams.get("level") ?? "";
    const factors = new URL(request.url).searchParams.get("factors") ?? "";
    const url = new URL(`${api}/stats/${level}/${category}/fips-value?`);
    url.searchParams.set("measure", measure);
    if (factors) url.searchParams.set("filters", factors);

    const actual: _StatsFipsValue = await (await fetch(url)).json();

    const desired: Statistic = {
      values: mapValues(actual.values, ({ value, aac }) => ({
        value: value ?? undefined,
        aac: aac ?? undefined,
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

    return response(desired);
  },

  "/location$": async () => {
    const url = new URL(`${api}/locations`);

    const actual: _Locations = await (await fetch(url)).json();

    const desired: Locations = Object.fromEntries(
      Object.values(actual)
        .flatMap((group) => Object.values(group))
        .map((id) => [id, {}]),
    );

    return response(desired);
  },

  "/location/(.*)$": async (request, location = "") => {
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

    return response(desired);
  },

  "/feature/(.*)$": async (request, feature = "") => {
    const url = new URL(`${api}/stats/by-county/${feature}`);

    const actual: _StatsByCounty = await (await fetch(url)).json();

    const desired: Feature = Object.fromEntries(
      Object.entries(actual.categories).flatMap(([category, { measures }]) =>
        Object.entries(measures).map(([measure, value]) => [
          `${category};${measure}`,
          {
            value: value.value ?? undefined,
            aac: value.aac ?? undefined,
            unit: value.unit ?? "count",
            state_value: value.state_value ?? undefined,
            state_aac: value.state_aac ?? undefined,
            order: value.order ?? undefined,
          },
        ]),
      ),
    );

    return response(desired);
  },
};

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
