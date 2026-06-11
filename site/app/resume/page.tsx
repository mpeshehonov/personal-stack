import fs from "fs";
import path from "path";
import type { Metadata } from "next";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import resume from "@/content/resume/resume.json";
import "./resume.css";

const resumeUrl = "https://mpeshekhonov.ru/resume";
const resumeTitle = `Резюме — ${resume.name}`;

export const metadata: Metadata = {
  title: resumeTitle,
  description: resume.summary,
  openGraph: {
    title: resumeTitle,
    description: resume.summary,
    url: resumeUrl,
    siteName: resume.name,
    locale: "ru_RU",
    type: "website",
  },
};

export default function ResumePage() {
  const md = fs.readFileSync(
    path.join(process.cwd(), "content/resume/resume.md"),
    "utf-8",
  );

  return (
    <article className="resume-page">
      <div className="resume-actions">
        <Link href="/resume/download" className="btn">
          Скачать PDF
        </Link>
      </div>
      <div className="resume-markdown">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>
      </div>
    </article>
  );
}
