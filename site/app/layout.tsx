import type { Metadata } from "next";
import Link from "next/link";
import resume from "@/content/resume/resume.json";
import "./globals.css";

const siteUrl = "https://mpeshekhonov.ru";
const title = `${resume.name} — ${resume.title}`;

export const metadata: Metadata = {
  title,
  description: resume.summary,
  metadataBase: new URL(siteUrl),
  openGraph: {
    title,
    description: resume.summary,
    url: siteUrl,
    siteName: resume.name,
    locale: "ru_RU",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>
        <header className="header">
          <nav>
            <Link href="/">Главная</Link>
            <Link href="/resume">Резюме</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer className="footer">
          <p>© {new Date().getFullYear()} {resume.name}</p>
        </footer>
      </body>
    </html>
  );
}
