import type { ID, Point } from "@/api";
import type { Geometry } from "geojson";
import { api, request } from "@/api";
import { mapValues } from "lodash";
import countyLabels from "./data/county-labels.json";
import geographyLabels from "./data/geography-labels.json";
import outreach from "./data/outreach.json";

export type Geographies = Record<ID, object>;

/** get high-level listing of all possible geographic levels */
export const getGeographies = async () => {
  /** build request */
  const url = new URL(`${api}/geography`);
  /** send request */
  const data = await request<Geographies>(url);

  /** add extra props */
  return mapValues(data, (value, key) => ({
    label: geographyLabels[key as keyof typeof geographyLabels] ?? "",
  }));
};

export type Geography = Record<
  ID,
  {
    geometry: Geometry;
    center: Point;
    description?: string;
  }
>;

/** get full details of geographic level */
export const getGeography = async (level: string) => {
  /** build request */
  const url = new URL(`${api}/geography/${level}`);

  /** send request */
  const data = await request<Geography>(url);

  /** add extra props */
  return mapValues(data, (value, key) => ({
    ...value,
    label: countyLabels[key as keyof typeof countyLabels],
    ...outreach[key as keyof typeof outreach],
  }));
};
