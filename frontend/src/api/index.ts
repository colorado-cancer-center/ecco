import type { FeatureCollection, Geometry } from "geojson";
import type { ValueOf } from "type-fest";
import { getValue } from "@/util/types";
import { mapValues } from "lodash";
import featureLabels from "./data/feature-labels.json";
import levelLabels from "./data/level-labels.json";
import locationGroups from "./data/location-groups.json";
import locationLabels from "./data/location-labels.json";
import events from "./data/outreach-events.json";
import fitKits from "./data/outreach-fit-kits.json";
import newspapers from "./data/outreach-newspapers.json";
import radonKits from "./data/outreach-radon-kits.json";
import outreach from "./data/outreach.json";
import sourceDetails from "./data/source-details.json";
import statisticLabels from "./data/statistic-labels.json";
import zipCodes from "./data/zip-codes.json";

/** api root (no trailing slash) */
export const api = import.meta.env.VITE_API;

console.debug("API:", api);

/** request cache */
const cache = new Map<string, Response>();

/** general request */
export const request = async <Response>(url: URL, options?: RequestInit) => {
  /** construct request */
  const request = new Request(url, options);
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
  return parsed as Response;
};

export type ID = string;

export type Point = [number, number];

/** value type/format */
export type Unit =
  | "count"
  | "percent"
  | "rate"
  | "dollar_amount"
  | "rank"
  | "least_most"
  | "ordinal";

export type Levels = Record<ID, object>;

/** get high-level listing of all possible geographic levels */
export const getLevels = async () => {
  /** build request */
  const url = new URL(`${api}/level`);
  /** send request */
  const data = await request<Levels>(url);

  return mapValues(data, (value, id) => ({
    /** add label */
    label: getValue(levelLabels, id) ?? id,
  }));
};

export type Level = FeatureCollection<
  Geometry,
  { center: Point; description?: string }
>;

/** get full details of geographic level */
export const getLevel = async (level: string) => {
  /** build request */
  const url = new URL(`${api}/level/${level}`);

  /** send request */
  const data = await request<Level>(url);

  return {
    ...data,
    /** all features of geographic level */
    features: data.features.map((feature) => ({
      ...feature,
      properties: {
        ...feature.properties,
        /** add label */
        label: [
          getValue(featureLabels, feature.id) ?? feature.id,
          getValue(levelLabels, level) ?? level,
        ].join(" "),
        /** add outreach properties */
        ...(getValue(outreach, feature.id) ?? {}),
      },
    })),
  };
};

export type Statistics = Record<
  ID,
  { levels: ID[]; factors: Record<string, string[]> }
>;

/** get high-level listing of all possible statistics */
export const getStatistics = async () => {
  /** build request */
  const url = new URL(`${api}/statistics`);

  /** send request */
  const data = await request<Statistics>(url);

  return mapValues(data, (value, id) => ({
    ...value,
    /** add label */
    label: getValue(statisticLabels, id) ?? id,
  }));
};

export type Statistic = {
  values: Record<ID, { value?: number | string; aac?: number | string }>;
  max?: number | string;
  min?: number | string;
  unit?: Unit;
  order?: string[];
  state?: number | string;
  source?: ID;
  state_source?: ID;
};

/** get specific statistic values for features of geographic level */
export const getStatistic = async (
  statistic: string,
  level: string,
  factors: Record<string, string>,
) => {
  /** build request */
  const url = new URL(`${api}/statistic/${statistic}`);
  const factorsString = Object.entries(factors || {})
    .map((entry) => entry.join(":"))
    .join(";");
  url.searchParams.set("level", level);
  url.searchParams.set("factors", factorsString);

  /** send request */
  const data = await request<Statistic>(url);

  return {
    ...data,
    /** add label */
    label: getValue(statisticLabels, statistic) ?? statistic,
    /** add source details */
    source: getValue(sourceDetails, data.source),
  };
};

export type Locations = Record<ID, object>;

/** extra locations stored in frontend */
const extraLocations: Record<string, Record<string, number>> = {
  events: events,
  "fit-kits": fitKits,
  "radon-kits": radonKits,
  newspapers: newspapers,
};

/** get high-level listing of all possible locations */
export const getLocations = async () => {
  /** build request */
  const url = new URL(`${api}/location`);
  /** send request */
  const data = await request<Locations>(url);

  /** add extra locations */
  for (const location of Object.keys(extraLocations)) data[location] = {};

  /** flat list */
  return Object.entries(locationGroups).flatMap(([group, locations]) => [
    { group },
    ...locations.map((location) => ({
      id: location,
      /** add label */
      label: getValue(locationLabels, location) ?? location,
    })),
  ]);
};

export type Location = FeatureCollection<
  Geometry,
  {
    org?: string;
    link?: string;
    address?: string;
    phone?: string;
    notes?: string;
    email?: string;
    district?: number;
    zip_code?: string;
    area_type?: string;
    representative?: string;
    party?: string;
    fips?: string;
    zip?: string;
    count?: number;
  }
>;

/** get full details of specific location */
export const getLocation = async (location: ID) => {
  /** build request */
  const url = new URL(`${api}/location/${location}`);
  let data: Location;

  /** intercept extra locations */
  if (location in extraLocations) {
    data = {
      type: "FeatureCollection",
      features: Object.entries(extraLocations[location] ?? {}).map(
        ([zip, count]) => {
          const [lat = 99999, long = 99999] = getValue(zipCodes, zip) ?? [];
          return {
            type: "Feature",
            geometry: { type: "Point", coordinates: [long, lat] },
            properties: { zip, count },
          };
        },
      ),
    };
  } else
    /** send request */
    data = await request<Location>(url);

  return {
    ...data,
    /** add label */
    features: data.features.map((feature) => ({
      ...feature,
      properties: {
        ...feature.properties,
        /** add label */
        label: getValue(locationLabels, location) ?? location,
      },
    })),
  };
};

export type Feature = object;

/** get full details of all statistics for feature of geographic level */
export const getFeature = async (feature: string, level = "county") => {
  /** build request */
  const url = new URL(`${api}/stats/by-${level}/${feature}`);
  /** send request */
  const data = await request<Feature>(url);

  return data;
};

/** get download all link */
export const getDownloadAll = () => `${api}/stats/download-all`;

/** get source citation */
export const getSourceCitation = (source: ValueOf<typeof sourceDetails>) =>
  [source.label, source.link].filter(Boolean).join("\n");
