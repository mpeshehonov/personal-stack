export type Availability = "open" | "busy";

export function parseAvailability(value?: string): Availability {
  return value === "busy" ? "busy" : "open";
}
