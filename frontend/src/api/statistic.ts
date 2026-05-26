import type { ID, Unit } from "./";
import { api, request } from "./";

export type Statistics = Record<
  ID,
  {
    levels: ID[];
    factors: Record<string, string[]>;
  }
>;

/** get high-level listing of all possible statistics */
export const getStatistics = async () => {
  /** build request */
  const url = new URL(`${api}/statistics`);

  /** send request */
  const data = await request<Statistics>(url);

  return data;
};

export type Statistic = {
  values: Record<
    ID,
    {
      value?: number | string | null;
      aac?: number | string | null;
    }
  >;
  max?: number | string;
  min?: number | string;
  unit: Unit;
  order?: string[];
  state?: number | string;
  source?: ID;
  state_source?: ID;
};

/** get specific statistic values for features of geographic level */
export const getStatistic = (
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
  const data = request<Statistic>(url);

  return data;
};
