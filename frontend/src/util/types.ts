/** get keys of object whose values match a certain type */
export type KeysOfValue<Data, Value> = keyof {
  [Key in keyof Data as Data[Key] extends Value ? Key : never]: never;
};

/**
 * expand type for intellisense
 * https://github.com/microsoft/TypeScript/issues/28508
 */
export type Expand<Type> = { [Key in keyof Type]: Type[Key] } & {};

/** update Prop in Object to include Type */
export type Update<
  Object extends object,
  Prop extends keyof Object,
  Type,
> = Omit<Object, Prop> & { [key in Prop]: Type | Object[Prop] };
