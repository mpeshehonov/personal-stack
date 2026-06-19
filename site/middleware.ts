import { NextRequest, NextResponse } from "next/server";

export const locales = ["ru", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "ru";

function getLocale(request: NextRequest): Locale {
  const cookie = request.cookies.get("locale")?.value;
  if (cookie && locales.includes(cookie as Locale)) {
    return cookie as Locale;
  }
  return defaultLocale;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".") // static files in public
  ) {
    return NextResponse.next();
  }

  const hasLocale = locales.some(
    (l) => pathname === `/${l}` || pathname.startsWith(`/${l}/`),
  );

  if (!hasLocale) {
    const locale = getLocale(request);
    const suffix = pathname === "/" ? "" : pathname;
    return NextResponse.redirect(new URL(`/${locale}${suffix}`, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
