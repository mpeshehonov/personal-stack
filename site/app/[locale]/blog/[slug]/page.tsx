import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  formatBlogDate,
  getAllBlogSlugs,
  getBlogPostBySlug,
} from "@/lib/blog";
import { getDictionary, localizedPath } from "@/lib/i18n";
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

export default async function BlogPostPage({ params }: Props) {
  const { slug, locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const post = getBlogPostBySlug(slug);
  if (!post) notFound();

  const backLabel = locale === "en" ? "All posts" : "Все записи";

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <Link
          href={localizedPath(locale, "/blog")}
          className="mb-4 inline-block text-sm text-ink-faint hover:text-accent"
        >
          ← {backLabel}
        </Link>
        <time className="font-mono text-xs text-ink-faint">
          {formatBlogDate(post.date)}
        </time>
        <h1 className="mb-4 mt-2 text-3xl font-bold text-ink sm:text-4xl">{post.title}</h1>
        <div className="flex flex-wrap gap-2">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-md bg-accent-soft px-2.5 py-1 text-xs font-medium text-accent"
            >
              {tag}
            </span>
          ))}
        </div>
      </header>
      <div className="prose-blog card p-6 sm:p-8">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
      </div>
      <p className="mt-8">
        <Link href={localizedPath(locale, "/")} className="text-sm text-ink-faint hover:text-accent">
          ← {dict.nav.home}
        </Link>
      </p>
    </article>
  );
}
