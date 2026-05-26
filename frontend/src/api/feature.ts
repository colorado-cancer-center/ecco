import { api, request } from "./";

export type Feature = object;

/** get full details of all statistics for feature of geographic level */
export const getFeature = async (feature: string, level = "county") => {
  /** build request */
  const url = new URL(`${api}/stats/by-${level}/${feature}`);
  /** send request */
  const data = await request<Feature>(url);

  return data;
};
