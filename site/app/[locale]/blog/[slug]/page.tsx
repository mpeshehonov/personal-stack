import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { BlogPostHeader } from "@/components/BlogPostHeader";
import {
  formatBlogDate,
  getAllBlogSlugs,
  getBlogPostBySlug,
} from "@/lib/blog";
import { localizedPath } from "@/lib/i18n";
import { buildPageMetadata } from "@/lib/metadata";
import type { Locale } from "@/middleware";

type Props = {
  params: Promise<{ locale: string; slug: string }>;
};

export async function generateStaticParams() {
  const slugs = getAllBlogSlugs();
  return ["ru", "en"].flatMap((locale) =>
    slugs.map((slug) => ({ locale, slug })),
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug, locale: raw } = await params;
  const locale = raw === "en" ? "en" : "ru";
  const post = getBlogPostBySlug(slug);
  if (!post) return {};

  return buildPageMetadata({
    title: post.title,
    description: post.excerpt,
    locale,
    path: `/blog/${slug}`,
    ogTitle: post.title,
    ogSubtitle: locale === "en" ? "Blog" : "Блог",
  });
}

export default async function BlogPostPage({ params }: Props) {
  const { slug, locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const post = getBlogPostBySlug(slug);
  if (!post) notFound();

  const backLabel = locale === "en" ? "All posts" : "Все записи";

  return (
    <article className="pb-20 pt-8">
      <BlogPostHeader
        href={localizedPath(locale, "/blog")}
        label={backLabel}
        date={formatBlogDate(post.date)}
        title={post.title}
        tags={post.tags}
      />
      <div className="prose-blog mx-auto max-w-3xl">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
      </div>
      <footer className="mx-auto mt-12 max-w-3xl border-t border-border pt-8">
        <Link
          href={localizedPath(locale, "/blog")}
          className="text-sm font-medium text-ink-muted transition hover:text-accent"
        >
          ← {backLabel}
        </Link>
      </footer>
    </article>
  );
}
