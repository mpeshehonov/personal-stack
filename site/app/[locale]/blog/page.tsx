import Link from "next/link";
import { formatBlogDate, getBlogPosts } from "@/lib/blog";
import { getDictionary, localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";

export default async function BlogPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const posts = getBlogPosts();

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <p className="section-label">{dict.sections.blog}</p>
        <h1 className="section-title mb-3">{dict.sections.blog}</h1>
        <p className="max-w-2xl text-ink-muted">{dict.sections.blogDesc}</p>
      </header>
      <div className="space-y-4">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={localizedPath(locale, `/blog/${post.slug}`)}
            className="card block transition hover:shadow-lift"
          >
            <time className="font-mono text-xs text-ink-faint">
              {formatBlogDate(post.date)}
            </time>
            <h2 className="mb-2 mt-1 text-xl font-semibold text-ink">{post.title}</h2>
            <p className="mb-3 text-sm text-ink-muted">{post.excerpt}</p>
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-md bg-surface-subtle px-2.5 py-1 text-xs text-ink-muted"
                >
                  {tag}
                </span>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </article>
  );
}
