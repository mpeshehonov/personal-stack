import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { notFound } from "next/navigation";
import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import { ContactCTA } from "@/components/ContactCTA";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { getDictionary } from "@/lib/i18n";
import { buildPersonJsonLd } from "@/lib/person-schema";
import { parseAvailability } from "@/lib/availability";
import { defaultLocale, locales, type Locale } from "@/middleware";
import "../globals.css";

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

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale: raw } = await params;
  const locale = (locales.includes(raw as Locale) ? raw : defaultLocale) as Locale;
  const t = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;
  const title = `${resume.name} — ${resume.title}`;

  return {
    title: { default: title, template: `%s — ${resume.name}` },
    description: t.meta.description,
    metadataBase: new URL("https://mpeshekhonov.ru"),
    openGraph: {
      title,
      description: t.meta.description,
      url: `https://mpeshekhonov.ru/${locale}`,
      siteName: resume.name,
      locale: locale === "en" ? "en_US" : "ru_RU",
      type: "website",
    },
    alternates: {
      canonical: `https://mpeshekhonov.ru/${locale}`,
      languages: {
        ru: "https://mpeshekhonov.ru/ru",
        en: "https://mpeshekhonov.ru/en",
      },
    },
  };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  if (!locales.includes(raw as Locale)) notFound();
  const locale = raw as Locale;
  const dict = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;
  const personJsonLd = buildPersonJsonLd(locale, resume);

  return (
    <html lang={locale} className={`${inter.variable} ${jetbrains.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');if(t==='dark')document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personJsonLd) }}
        />
      </head>
      <body className="overflow-x-hidden font-sans">
        <Header locale={locale} dict={dict} className="print:hidden" />
        <main className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8 print:max-w-none print:px-0">
          {children}
        </main>
        <div className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8 print:hidden">
          <ContactCTA locale={locale} dict={dict} />
        </div>
        <Footer
          locale={locale}
          dict={dict}
          name={resume.name}
          availability={parseAvailability(resume.availability)}
          className="print:hidden"
        />
      </body>
    </html>
  );
}
