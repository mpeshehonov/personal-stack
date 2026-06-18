import type { Metadata } from "next";
import { ogImageUrl } from "@/lib/og";

const SITE_URL = "https://mpeshekhonov.ru";

type PageMetaInput = {
  title: string;
  description: string;
  locale: string;
  path: string;
  ogTitle?: string;
  ogSubtitle?: string;
};

export function buildPageMetadata({
  title,
  description,
  locale,
  path,
  ogTitle,
  ogSubtitle,
}: PageMetaInput): Metadata {
  const pageUrl = `${SITE_URL}/${locale}${path}`;
  const image = ogImageUrl({
    title: ogTitle ?? title,
    subtitle: ogSubtitle,
    locale,
  });

  return {
    title,
    description,
    openGraph: {
      title: ogTitle ?? title,
      description,
      url: pageUrl,
      images: [{ url: image, width: 1200, height: 630, alt: title }],
    },
    twitter: {
      card: "summary_large_image",
      title: ogTitle ?? title,
      description,
      images: [image],
    },
  };
}
