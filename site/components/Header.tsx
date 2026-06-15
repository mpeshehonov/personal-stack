"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";

type Props = {
  locale: Locale;
  dict: Dictionary;
  className?: string;
};

const navKeys = [
  { href: "/", key: "home" as const },
  { href: "/projects", key: "projects" as const },
  { href: "/blog", key: "blog" as const },
  { href: "/resume", key: "resume" as const },
];

export function Header({ locale, dict, className = "" }: Props) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const otherLocale: Locale = locale === "ru" ? "en" : "ru";
  const pathWithoutLocale = pathname.replace(/^\/(ru|en)/, "") || "/";

  return (
    <header className={`sticky top-0 z-50 border-b border-border bg-surface/90 backdrop-blur-md ${className}`}>
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          href={localizedPath(locale, "/")}
          className="shrink-0 font-mono text-sm font-semibold tracking-tight text-ink"
        >
          mpeshekhonov
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Main">
          {navKeys.map(({ href, key }) => {
            const full = localizedPath(locale, href);
            const active =
              href === "/"
                ? pathname === full
                : pathname === full || pathname.startsWith(`${full}/`);
            return (
              <Link
                key={href}
                href={full}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-accent-soft text-accent"
                    : "text-ink-muted hover:bg-surface-subtle hover:text-ink"
                }`}
              >
                {dict.nav[key]}
              </Link>
            );
          })}
          <Link
            href={localizedPath(otherLocale, pathWithoutLocale)}
            className="ml-2 rounded-lg border border-border px-2.5 py-1.5 font-mono text-xs font-semibold text-ink-muted transition hover:border-border-strong hover:text-ink"
            aria-label={otherLocale === "en" ? "English" : "Русский"}
          >
            {dict.lang[otherLocale]}
          </Link>
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          <Link
            href={localizedPath(otherLocale, pathWithoutLocale)}
            className="rounded-lg border border-border px-2 py-1 font-mono text-xs font-semibold text-ink-muted"
          >
            {dict.lang[otherLocale]}
          </Link>
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface text-ink"
            aria-expanded={open}
            aria-controls="mobile-nav"
            onClick={() => setOpen((v) => !v)}
          >
            <span className="sr-only">{open ? dict.nav.close : dict.nav.menu}</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
              {open ? (
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              ) : (
                <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <nav
          id="mobile-nav"
          className="border-t border-border bg-surface px-4 py-4 md:hidden"
          aria-label="Mobile"
        >
          <ul className="flex flex-col gap-1">
            {navKeys.map(({ href, key }) => {
              const full = localizedPath(locale, href);
              return (
                <li key={href}>
                  <Link
                    href={full}
                    className="block rounded-xl px-3 py-3 text-base font-medium text-ink hover:bg-surface-subtle"
                  >
                    {dict.nav[key]}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      )}
    </header>
  );
}
