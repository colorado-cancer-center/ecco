/** get keys of object whose values match a certain type */
export type KeysOfValue<Data, Value> = keyof {
  [Key in keyof Data as Data[Key] extends Value ? Key : never]: never;
};
