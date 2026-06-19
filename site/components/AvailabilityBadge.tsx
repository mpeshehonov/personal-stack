import type { Dictionary } from "@/lib/i18n";
import type { Availability } from "@/lib/availability";

type Props = {
  status: Availability;
  dict: Dictionary;
  size?: "sm" | "md";
};

const dotColor: Record<Availability, string> = {
  open: "bg-emerald-500",
  asap: "bg-emerald-500",
  busy: "bg-amber-500",
};

export function AvailabilityBadge({ status, dict, size = "md" }: Props) {
  const label =
    status === "busy"
      ? dict.footer.availabilityBusy
      : status === "asap"
        ? dict.footer.availabilityAsap
        : dict.footer.availabilityOpen;
  const sizeClass =
    size === "sm"
      ? "px-2.5 py-1 text-xs"
      : "px-3 py-1.5 text-sm";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border border-border bg-surface-subtle font-medium text-ink-muted ${sizeClass}`}
    >
      <span
        className={`inline-block h-2 w-2 shrink-0 rounded-full ${dotColor[status]}`}
        aria-hidden
      />
      {label}
    </span>
  );
}
