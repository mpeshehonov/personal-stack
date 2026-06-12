import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import Link from "next/link";

type Props = {
  locale: Locale;
  dict: Dictionary;
  name: string;
};

export function Footer({ locale, dict, name }: Props) {
  return (
    <footer className="mt-20 border-t border-border bg-surface py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-4 text-center text-sm text-ink-faint sm:px-6 lg:px-8">
        <p>
          © {new Date().getFullYear()} {name}
        </p>
        <p className="font-mono text-xs">{dict.footer.built}</p>
        <Link href={localizedPath(locale, "/resume")} className="text-accent hover:underline">
          {dict.nav.resume}
        </Link>
      </div>
    </footer>
  );
}
