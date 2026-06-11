import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import resume from "@/content/resume/resume.json";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin", "cyrillic"],
  variable: "--font-mono",
  display: "swap",
});

const siteUrl = "https://mpeshekhonov.ru";
const title = `${resume.name} — ${resume.title}`;
const description =
  "Senior Frontend / Fullstack разработчик. Next.js, React, TypeScript, Telegram Mini Apps, real-time и сложные интерфейсы.";

export const metadata: Metadata = {
  title: {
    default: title,
    template: `%s — ${resume.name}`,
  },
  description,
  metadataBase: new URL(siteUrl),
  openGraph: {
    title,
    description,
    url: siteUrl,
    siteName: resume.name,
    locale: "ru_RU",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
  },
  alternates: {
    canonical: siteUrl,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="font-sans">
        <Header />
        <main className="mx-auto max-w-5xl px-4 sm:px-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
