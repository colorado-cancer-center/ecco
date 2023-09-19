import type { Feature, Geometry as GeoJsonGeometry } from "geojson";
import { mapValues, startCase } from "lodash";

// api root
const api = import.meta.env.VITE_API;

console.info("API:", api);

// request cache
const cache = new Map();

// general request
export async function request<T>(url: string) {
  // construct request
  const request = new Request(url);
  // unique request id for caching
  const id = JSON.stringify(request, ["url", "method", "headers"]);
  // get response from cache or make new request
  const response = cache.get(id) || (await fetch(request));
  // check status code
  if (!response.ok) throw Error("Response not OK");
  // parse response
  const parsed = await response.clone().json();
  // set cache for next time
  if (request.method === "GET") cache.set(id, response);
  return parsed as T;
}

// response from counties/tract api endpoints
type _Geometry = {
  [key: string]: string | number | undefined;

  full?: string;
  name?: string;
  fips?: string;
  us_fips?: string;
  objectid: number;
  ogc_fid: number;
  wkb_geometry: string;
}[];

// get geojson from geography data
export async function getGeometry(type: string, idField: string) {
  const data = await request<_Geometry>(`${api}/${type}`);

  // transform data into desired format
  return data.map(
    ({ wkb_geometry, ...d }) =>
      ({
        type: "Feature",
        geometry: JSON.parse(wkb_geometry) as GeoJsonGeometry,
        properties: {
          ...d,
          id: d[idField],
          name: d.full || d.name || "",
        },
      }) satisfies Feature,
  );
}

export type Geometry = Awaited<ReturnType<typeof getGeometry>>;

// response from measures api endpoint
type _Measures = {
  [key: string]: {
    [key: string]: {
      display_name: string;
      measures: { name: string; display_name: string }[];
    };
  };
};

// specific "level" of data
export type Facet = {
  [key: string]: {
    id: string;
    name: string;
    children?: Facet;
  };
};

// get hierarchical list of geographic levels, variable categories, and variables
export async function getMeasures() {
  const data = await request<_Measures>(`${api}/stats/measures`);

  // transform data into desired format
  return mapValues(data, (value, key) => ({
    // geographic level
    id: key,
    name: startCase(key),
    children: mapValues(value, (value, key) => ({
      // variable category
      id: key,
      name: value.display_name,
      children: Object.fromEntries(
        value.measures.map((entry) => [
          // variable
          entry.name,
          {
            id: entry.name,
            name: entry.display_name,
          },
        ]),
      ),
    })),
  })) satisfies Facet;
}

export type Measures = Awaited<ReturnType<typeof getMeasures>>;

type _Measure = {
  max: number;
  min: number;
  values: { [key: number]: number };
};

// get variable data for map
export async function getValues(
  level: string,
  category: string,
  variable: string,
) {
  const params = new URLSearchParams({ measure: variable });
  const data = await request<_Measure>(
    `${api}/stats/${level}/${category}/fips-value?` + params,
  );
  return data;
}

export type Values = Awaited<ReturnType<typeof getValues>>;
