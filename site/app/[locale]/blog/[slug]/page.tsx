import { redirect } from "next/navigation";
import type { Locale } from "@/middleware";
import { localizedPath } from "@/lib/i18n";

/** Blog temporarily hidden — neuroslop. */
export default async function BlogPostRedirect({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  redirect(localizedPath(locale, "/"));
}
