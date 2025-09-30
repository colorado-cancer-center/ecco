import type { FeatureCollection, Geometry } from "geojson";
import { find, findKey, mapValues } from "lodash";
import type { ValueOf } from "type-fest";
import outreachCounty1 from "./temp/outreach-county-1.json";
import outreachCounty2 from "./temp/outreach-county-2.json";
import outreachCounty3 from "./temp/outreach-county-3.json";
import outreachCounty4 from "./temp/outreach-county-4.json";
import outreachEvents from "./temp/outreach-events.json";
import outreachFitKits from "./temp/outreach-fit-kits.json";
import outreachNewspapers from "./temp/outreach-newspapers.json";
import outreachRadonKits from "./temp/outreach-radon-kits.json";
import zipCodeLookup from "./temp/zip-code-lookup.json";

/** api root (no trailing slash) */
const api = import.meta.env.VITE_API;

console.debug("API:", api);

/** request cache */
const cache = new Map<string, Response>();

/** general request */
export const request = async <T>(
  url: string | URL,
  params: Record<string, string | string[]> = {},
) => {
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
};

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
export const getFacets = async () => {
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
};

export type Facets = Awaited<ReturnType<typeof getFacets>>;

/** response from location list api endpoint */
type _LocationList = {
  [key: string]: { [key: string]: string };
};

/** extra hard-coded location list entries */
/** TEMPORARY: should eventually come from backend */
export const extraLocationList = {
  "Outreach and Interventions": {
    Events: "outreach-events",
    Newspapers: "outreach-newspapers",
    "FIT Kits": "outreach-fit-kits",
    "Radon Kits": "outreach-radon-kits",
    "2morrow": "outreach-2morrow-county",
  },
} as const;

/** get listing/metadata of locations */
export const getLocationList = async () => {
  const data = await request<_LocationList>(`${api}/locations`);
  return { ...extraLocationList, ...data };
};

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
  /** base */
  id?: string | number;
  name?: string;
  label?: string;
  fips?: string;
  us_fips?: string;
  objectid?: number;
  ogc_fid?: number;
  cent_lat?: number;
  cent_long?: number;

  /* health statistics region (HSR) addt'l data */
  counties?: string; // counties within the HSR
  hs_region?: string; // HSR number

  /** outreach */
  fit_kits?: number;
  radon_kits?: number;
  total_kits?: number;
  community_events?: number;
  health_fairs?: number;
  educational_talks?: number;
  radio_talks?: number;
  school_church_events?: number;
  total_events?: number;
  womens_wellness_centers?: number;
  "2morrow_signups"?: number;
  has_fit_kits?: boolean;
  has_radon_kits?: boolean;
  has_both_kits?: boolean;
  has_any_activity?: boolean;
  has_2morrow?: boolean;
  has_womens_wellness_center?: boolean;
  has_all?: boolean;
};

/** get geojson from geography data */
export const getGeo = async (
  type: "counties" | "tracts" | "healthregions",
  idField: string,
): Promise<FeatureCollection<Geometry, GeoProps>> => {
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

          /** include extra per-county data */
          /** TEMPORARY: should eventually come from backend */
          ...(find(outreachCounty1, ["county", name]) ?? {}),
          ...(find(outreachCounty2, ["county", name]) ?? {}),
          ...(find(outreachCounty3, ["county", name]) ?? {}),
          ...(find(outreachCounty4, ["county", name]) ?? {}),
        },
      };
    }),
  };
};

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
  state_source?: string;
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
export const getValues = async (
  level: string,
  category: string,
  measure: string,
  filters: { [key: string]: string },
) => {
  const filtersString = Object.entries(filters || {})
    .map((entry) => entry.join(":"))
    .join(";");

  const data = await request<_Values>(
    `${api}/stats/${level}/${category}/fips-value?`,
    { measure, ...(filtersString && { filters: filtersString }) },
  );

  return data;
};

export type Values = Awaited<ReturnType<typeof getValues>>;

/** response from locations api endpoint */
type _Location = {
  id: string;
  name: string;
  category_id: string;
  geometry_json: FeatureCollection<Geometry, LocationProps>;
};

/** extra hard-coded location data */
/** TEMPORARY: should eventually come from backend */
const extraLocationData = {
  "outreach-events": outreachEvents,
  "outreach-newspapers": outreachNewspapers,
  "outreach-fit-kits": outreachFitKits,
  "outreach-radon-kits": outreachRadonKits,
} satisfies Partial<
  Record<
    ValueOf<(typeof extraLocationList)["Outreach and Interventions"]>,
    unknown
  >
>;

/** get locations (markers, highlighted areas, etc) */
export const getLocation = async (
  id: string,
): Promise<FeatureCollection<Geometry, LocationProps>> => {
  /** include extra location data */
  /** TEMPORARY: should eventually come from backend */
  if (id in extraLocationData) {
    /** get label version of id */
    const type =
      findKey(extraLocationList["Outreach and Interventions"], id) ?? "";

    return {
      type: "FeatureCollection",
      features: extraLocationData[id as keyof typeof extraLocationData].map(
        ({ zip, count }) => {
          const { lat = 99999, lng = 99999 } =
            zipCodeLookup[zip as keyof typeof zipCodeLookup];
          return {
            type: "Feature",
            geometry: { type: "Point", coordinates: [lng, lat] },
            properties: { type, zip, count },
          };
        },
      ),
    };
  }

  const data = await request<_Location>(`${api}/locations/${id}`);

  /** add type of location, i.e. label version of id */
  const type = data.name;
  data.geometry_json.features.forEach(
    (feature) => (feature.properties.type = type),
  );

  return data.geometry_json;
};

export type Location = Awaited<ReturnType<typeof getLocation>>;

/** get data download link */
export const getDownload = (
  level: string,
  category: string,
  measure?: string,
) => {
  const url = new URL(`${api}/stats/${level}/${category}/as-csv`);
  if (measure) url.searchParams.set(measure, measure);
  return url.toString();
};

/** get download all link */
export const getDownloadAll = () => `${api}/stats/download-all`;

/** location geojson properties fields */
export type LocationProps = {
  type?: string;
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
  zip?: string;
  count?: number;
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
