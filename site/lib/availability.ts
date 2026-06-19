export type Availability = "open" | "busy" | "asap";

export function parseAvailability(value?: string): Availability {
  if (value === "busy") return "busy";
  if (value === "asap") return "asap";
  return "open";
}
