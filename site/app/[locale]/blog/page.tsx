import { redirect } from "next/navigation";
import type { Locale } from "@/middleware";
import { localizedPath } from "@/lib/i18n";

/** Blog temporarily hidden — neuroslop; keep route as redirect so old links don't 404 harshly. */
export default async function BlogIndexRedirect({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  redirect(localizedPath(locale, "/"));
}
