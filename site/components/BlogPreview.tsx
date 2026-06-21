import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import type { BlogPostMeta } from "@/lib/blog";
import { formatBlogDate } from "@/lib/blog";
import { FadeIn } from "./FadeIn";

type Props = {
  locale: Locale;
  dict: Dictionary;
  posts: BlogPostMeta[];
};

export function BlogPreview({ locale, dict, posts }: Props) {
  if (posts.length === 0) return null;

  return (
    <FadeIn className="section">
      <div className="section-intro">
        <div>
          <p className="section-label">{dict.sections.latestBlog}</p>
          <h2 className="section-title">{dict.sections.latestBlog}</h2>
          <p className="section-desc">{dict.sections.latestBlogDesc}</p>
        </div>
        <Link
          href={localizedPath(locale, "/blog")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {dict.sections.allPosts} →
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {posts.map((post, index) => (
          <FadeIn key={post.slug} delay={index * 0.08}>
            <Link
              href={localizedPath(locale, `/blog/${post.slug}`)}
              className="card block h-full transition hover:shadow-lift"
            >
              <time className="font-mono text-xs text-ink-faint">
                {formatBlogDate(post.date)}
              </time>
              <h3 className="mb-2 mt-1 text-lg font-semibold text-ink">{post.title}</h3>
              <p className="text-sm text-ink-muted">{post.excerpt}</p>
            </Link>
          </FadeIn>
        ))}
      </div>
    </FadeIn>
  );
}
