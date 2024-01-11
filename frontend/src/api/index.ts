import * as d3 from "d3";
import type { FeatureCollection, Geometry } from "geojson";
import { mapValues } from "lodash";
import cancerCenterLocations from "./cancer-center-locations.json";
import cancerInFocusLocations from "./cancer-in-focus-locations.json";

/** api root (no trailing slash) */
const api = import.meta.env.VITE_API;

console.info("API:", api);

/** request cache */
const cache = new Map();

/** general request */
export async function request<T>(url: string) {
  /** construct request */
  const request = new Request(url);
  /** unique request id for caching */
  const id = JSON.stringify(request, ["url", "method", "headers"]);
  /** get response from cache or make new request */
  const response = cache.get(id) || (await fetch(request));
  /** check status code */
  if (!response.ok) throw Error("Response not OK");
  /** parse response */
  const parsed = await response.clone().json();
  /** set cache for next time */
  if (request.method === "GET") cache.set(id, response);
  return parsed as T;
}

/** response from counties/tract api endpoints */
type _Data = {
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
type DataProps = {
  id: string | number | undefined;
  name: string;
  full?: string | undefined;
  fips?: string | undefined;
  us_fips?: string | undefined;
  objectid: number;
  ogc_fid: number;
};

/** get geojson from geography data */
export async function getData(
  type: string,
  idField: string,
): Promise<FeatureCollection<Geometry, DataProps>> {
  const data = await request<_Data>(`${api}/${type}`);

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

export type Data = Awaited<ReturnType<typeof getData>>;

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
  };
};

/** get hierarchical list of geographic levels, measure categories, and measures */
export async function getFacets() {
  const data = await request<_Facets>(`${api}/stats/measures`);

  /** transform data into desired format */
  return mapValues(data, ({ label, categories }, key) => ({
    /** geographic level */
    id: key,
    label,
    list: mapValues(categories, ({ label, measures }, key) => ({
      /** measure category */
      id: key,
      label,
      list: mapValues(measures, ({ label }, key) => ({
        /** measure */
        id: key,
        label,
      })),
    })),
  })) satisfies Facet;
}

export type Facets = Awaited<ReturnType<typeof getFacets>>;

/** response from values api endpoint */
type _Values = {
  /** range of values for specified measure */
  max: number;
  min: number;
  /** map of feature id to measure value */
  values: { [key: string]: { value: number; aac?: number | null } };
};

/** get values data */
export async function getValues(
  level: string,
  category: string,
  measure: string,
) {
  const params = new URLSearchParams({ measure });
  const data = await request<_Values>(
    `${api}/stats/${level}/${category}/fips-value?` + params,
  );

  const values = Object.values(data.values).map(({ value }) => value);

  /** calculate stats */
  return {
    min: d3.min(values),
    max: d3.max(values),
    mean: d3.mean(values),
    median: d3.median(values),
    values: data.values,
  };
}

export type Values = Awaited<ReturnType<typeof getValues>>;

/** get data download link */
export function getDataDownload(
  level: string,
  category: string,
  measure: string,
) {
  return `${api}/stats/${level}/${category}/as-csv?measure=${measure}`;
}

/** location geojson properties fields */
type LocationProps = {
  name?: string;
  org?: string;
  link?: string;
  address?: string;
  phone?: string;
  notes?: string;
  fips?: string;
};

/** response from locations api endpoint */
type _Locations = {
  [key: string]: {
    label: string;
    features: FeatureCollection<Geometry, LocationProps>;
  };
};

/** get locations (markers, highlighted areas, etc) */
export async function getLocations() {
  // const data = await request<_Locations>(`${api}/locations`);

  const data =
    /** merge together, assume no overlap in keys */
    {
      ...cancerInFocusLocations,
      ...cancerCenterLocations,
    } as _Locations;

  return data;
}

export type Locations = Awaited<ReturnType<typeof getLocations>>;
