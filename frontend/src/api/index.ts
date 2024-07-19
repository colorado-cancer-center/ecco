import * as d3 from "d3";
import type { FeatureCollection, Geometry } from "geojson";
import { mapValues } from "lodash";
import type { ExplicitScale } from "@/components/AppMap.vue";

/** api root (no trailing slash) */
const api = import.meta.env.VITE_API;

console.debug("API:", api);

/** request cache */
const cache = new Map<string, Response>();

/** general request */
export async function request<T>(
  url: string | URL,
  params: Record<string, string | string[]> = {},
) {
  /** make url object */
  url = new URL(url);
  /** construct params */
  for (const [key, value] of Object.entries(params))
    for (const param of [value].flat()) url.searchParams.append(key, param);
  /** construct request */
  const request = new Request(url);
  /** unique request id for caching */
  const id = JSON.stringify(request, ["url", "method", "headers"]);
  /** get response from cache */
  const cached = cache.get(id);
  /** log info */
  const log = `(${cached ? "cached" : "new"}) ${url}`;
  console.debug(`📞 Request ${log}`, { request });
  /** make new request */
  const response = cached ?? (await fetch(request));
  /** check status code */
  if (!response.ok) throw Error("Response not OK");
  /** parse response */
  const parsed = await response.clone().json();
  console.debug(`📣 Response ${log}`, { response, parsed });
  /** set cache for next time */
  if (request.method === "GET") cache.set(id, response);
  return parsed as T;
}

/** response from facets api endpoint */
type _Facets = {
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

/** specific "level" of data */
export type Facet = {
  [key: string]: {
    id: string;
    label: string;
    list?: Facet;
    factors?: {
      [key: string]: {
        label: string;
        default: string;
        values: { [key: string]: string };
      };
    };
  };
};

/** get hierarchical list of geographic levels, measure categories, and measures */
export async function getFacets() {
  const data = await request<_Facets>(`${api}/stats/measures`);

  /** transform data into desired format */
  return mapValues(data, ({ label, categories }, id) => ({
    /** geographic level */
    id,
    label,
    list: mapValues(categories, ({ label, measures }, id) => ({
      /** measure category */
      id,
      label,
      list: mapValues(measures, ({ label, factors }, id) => ({
        /** measure */
        id,
        label,
        factors,
      })),
    })),
  })) satisfies Facet;
}

export type Facets = Awaited<ReturnType<typeof getFacets>>;

type _LocationList = {
  [key: string]: { [key: string]: string };
};

/** get listing/metadata of locations */
export async function getLocationList() {
  const data = await request<_LocationList>(`${api}/locations`);
  return data;
}

export type LocationList = Awaited<ReturnType<typeof getLocationList>>;

/** response from counties/tract api endpoints */
type _Geo = {
  [key: string]: string | number | undefined;

  full?: string;
  name?: string;
  fips?: string;
  us_fips?: string;
  objectid: number;
  ogc_fid: number;
  wkb_geometry: string;
}[];

/** data geojson properties fields */
export type GeoProps = {
  id: string | number | undefined;
  name: string;
  full?: string | undefined;
  fips?: string | undefined;
  us_fips?: string | undefined;
  objectid: number;
  ogc_fid: number;
};

/** get geojson from geography data */
export async function getGeo(
  type: string,
  idField: string,
): Promise<FeatureCollection<Geometry, GeoProps>> {
  const data = await request<_Geo>(`${api}/${type}`);

  /** transform data into desired format */
  return {
    type: "FeatureCollection",
    features: data.map(({ wkb_geometry, ...d }) => ({
      type: "Feature",
      geometry: JSON.parse(wkb_geometry) as Geometry,
      properties: {
        ...d,
        id: d[idField],
        name: d.full || d.name || "",
      },
    })),
  };
}

export type Geo = Awaited<ReturnType<typeof getGeo>>;

/** value type/format */
export type Unit =
  | "percent"
  | "count"
  | "rate"
  | "dollar_amount"
  | "rank"
  | "ordinal"
  | "least_most"
  | null;

/** response from values api endpoint */
type _Values = {
  /** range of values for specified measure */
  max: number;
  min: number;
  /** map of feature id to measure value */
  values: { [key: string]: { value: number; aac?: number | null } };
  unit: Unit;
};

/** get values data */
export async function getValues(
  level: string,
  category: string,
  measure: string,
  filters: { [key: string]: string },
) {
  const filtersString = Object.entries(filters || {})
    .map((entry) => entry.join(":"))
    .join(";");

  const data = await request<_Values>(
    `${api}/stats/${level}/${category}/fips-value?`,
    { measure, ...(filtersString && { filters: filtersString }) },
  );

  const values = Object.values(data.values).map(({ value }) => value);

  /** calculate stats */
  const stats = {
    min: d3.min(values) || 0,
    max: d3.max(values) || 0,
    mean: d3.mean(values) || 0,
    median: d3.median(values) || 0,
    values: data.values,
    unit: data.unit,
  };

  /** if missing data, return empty */
  if (!values.length) return;

  /** define explicit scale for certain data */
  let explicitScale: ExplicitScale;
  if (data.unit === "ordinal")
    explicitScale = { 1: "Falling", 2: "Stable", 3: "Rising" };

  return { ...stats, explicitScale };
}

export type Values = Awaited<ReturnType<typeof getValues>>;

/** response from locations api endpoint */
type _Location = {
  id: string;
  name: string;
  category_id: string;
  geometry_json: FeatureCollection<Geometry, LocationProps>;
};

/** get locations (markers, highlighted areas, etc) */
export async function getLocation(id: string) {
  const data = await request<_Location>(`${api}/locations/${id}`);
  return data.geometry_json;
}

export type Location = Awaited<ReturnType<typeof getLocation>>;

/** get data download link */
export function getDownload(level: string, category: string, measure?: string) {
  const url = new URL(`${api}/stats/${level}/${category}/as-csv`);
  if (measure) url.searchParams.set(measure, measure);
  return url.toString();
}

/** get download all link */
export function getDownloadAll() {
  return `${api}/stats/download-all`;
}

/** location geojson properties fields */
export type LocationProps = {
  name?: string;
  org?: string;
  link?: string;
  address?: string;
  phone?: string;
  notes?: string;
  email?: string;
  district?: number;
  representative?: string;
  party?: string;
  fips?: string;
};
