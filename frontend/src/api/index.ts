import type { FeatureCollection, Geometry, Point } from "geojson";
import { mapValues } from "lodash";
import outreach1 from "./outreach-1.json";
import outreach2 from "./outreach-2.json";

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
  const log = `(${cached ? "🗄️ cached" : "✨ new"}) ${url}`;
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

/** response from location list api endpoint */
type _LocationList = {
  [key: string]: { [key: string]: string };
};

/** get listing/metadata of locations */
export async function getLocationList() {
  const data = await request<_LocationList>(`${api}/locations`);
  return { Outreach: { Outreach: "outreach" }, ...data };
}

export type LocationList = Awaited<ReturnType<typeof getLocationList>>;

/** response from counties/tract api endpoints */
type _Geo = {
  [key: string]: string | number | undefined;

  full?: string;
  name?: string;
  fips?: string;
  us_fips?: string;
  objectid?: number;
  ogc_fid?: number;
  wkb_geometry: string;
  cent_lat?: number;
  cent_long?: number;
}[];

/** data geojson properties fields */
export type GeoProps = {
  id?: string | number;
  name?: string;
  label?: string;
  fips?: string;
  us_fips?: string;
  objectid?: number;
  ogc_fid?: number;
  cent_lat?: number;
  cent_long?: number;
};

/** get geojson from geography data */
export async function getGeo(
  type: "counties" | "tracts",
  idField: string,
): Promise<FeatureCollection<Geometry, GeoProps>> {
  const data = await request<_Geo>(`${api}/${type}`);

  /** transform data into desired format */
  return {
    type: "FeatureCollection",
    features: data.map(({ wkb_geometry, full, ...d }) => {
      const geometry = JSON.parse(wkb_geometry) as Geometry;
      const name = full || d.name || "";

      return {
        type: "Feature",
        geometry,
        properties: {
          ...d,
          id: d[idField],
          name,
          label: name.replace(/county/i, ""),
        },
      };
    }),
  };
}

export type Geo = Awaited<ReturnType<typeof getGeo>>;

/** value type/format */
export type Unit =
  | "count"
  | "percent"
  | "rate"
  | "dollar_amount"
  | "rank"
  | "least_most"
  | "ordinal"
  | null;

/** response from values api endpoint */
type _Values = {
  /** range of values for specified measure */
  max: number | string;
  min: number | string;
  /** "global" value */
  state?: number | string;
  /** map of feature id to measure value */
  values: {
    [key: string]: { value: number | string; aac?: number | string };
  };
  /** unit info */
  unit: Unit;
  order?: string[];
  /** where data came from */
  source?: string;
  source_url?: string;
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

  return data;
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
  if (id === "outreach") return await getOutreach();

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
  num_fit?: number;
  num_radon?: number;
  total_kits?: number;
  num_com_event?: number;
  num_hf?: number;
  num_educ?: number;
  num_radio?: number;
  num_school?: number;
  total_events?: number;
  fit?: boolean;
  radon?: boolean;
  both_kits?: boolean;
  any_activity?: boolean;
  "2m"?: boolean;
  wwc?: boolean;
  all?: boolean;
};

/** response from county data api endpoint */
type _CountyData = {
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

/** get all data for particular county */
export const getCountyData = (id: string) =>
  request<_CountyData>(`${api}/stats/by-county/${id}`);

/** get per-county ecco outreach data */
/** temporary, should eventually come from backend */
export const getOutreach = async (): Promise<
  FeatureCollection<Point, LocationProps>
> => {
  /** get county geo data */
  const geo = (await getGeo("counties", "us_fips")).features;

  /** outreach data lookup */
  const outreach: Record<string, LocationProps> =
    /** initialize with county names from geo data */
    Object.fromEntries(geo.map((feature) => [feature.properties.name, {}]));

  /** combine outreach tables */
  for (const file of [outreach1, outreach2])
    for (const { county, ...rest } of file)
      if (county in outreach)
        /** assign county outreach props */
        outreach[county] = { ...outreach[county], ...rest };

  return {
    type: "FeatureCollection",
    features: geo.map(({ properties, ...feature }) => ({
      ...feature,
      geometry: {
        /** use county centroid point instead of county boundary polygon */
        type: "Point",
        coordinates: [properties.cent_long ?? 0, properties.cent_lat ?? 0],
      },
      /** get all outreach props for county */
      properties: properties.name ? (outreach[properties.name] ?? {}) : {},
    })),
  };
};
