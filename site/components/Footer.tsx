import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import Link from "next/link";
import { AvailabilityBadge } from "./AvailabilityBadge";
import { VisitCounter } from "./VisitCounter";
import type { Availability } from "@/lib/availability";

type Props = {
  locale: Locale;
  dict: Dictionary;
  name: string;
  availability: Availability;
  className?: string;
};

export function Footer({ locale, dict, name, availability, className = "" }: Props) {
  return (
    <footer className={`mt-20 border-t border-border bg-surface py-10 ${className}`}>
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-4 text-center text-sm text-ink-faint sm:px-6 lg:px-8">
        <AvailabilityBadge status={availability} dict={dict} size="sm" />
        <p>
          © {new Date().getFullYear()} {name}
        </p>
        <p className="font-mono text-xs">{dict.footer.built}</p>
        <VisitCounter label={dict.footer.visits} />
        <Link href={localizedPath(locale, "/resume")} className="text-accent hover:underline">
          {dict.nav.resume}
        </Link>
      </div>
    </footer>
  );
}
