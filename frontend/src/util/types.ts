/** type-safe lookup of value on object (avoids in-situ casting object or keys) */
export const getValue = <Value>(
  object: Record<PropertyKey, Value>,
  key: PropertyKey | undefined,
) => {
  /** if key defined and exists in object */
  if (key && key in object)
    /** return value, maintaining original type */
    return object[key] as Value;
  /** otherwise, return undefined */
};
