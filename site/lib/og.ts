const SITE_URL = "https://mpeshekhonov.ru";

export function ogImageUrl(params: {
  title: string;
  subtitle?: string;
  locale?: string;
}): string {
  const url = new URL("/api/og", SITE_URL);
  url.searchParams.set("title", params.title);
  if (params.subtitle) url.searchParams.set("subtitle", params.subtitle);
  if (params.locale) url.searchParams.set("locale", params.locale);
  return url.toString();
}
