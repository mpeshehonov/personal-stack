import type { Metadata } from "next";
import Link from "next/link";
import { formatBlogDate, getBlogPosts } from "@/lib/blog";

export const metadata: Metadata = {
  title: "Блог",
  description:
    "Заметки о разработке, self-hosted инфраструктуре и AI-агентах.",
  openGraph: {
    title: "Блог — Максим Пешехонов",
    description:
      "Заметки о разработке, self-hosted инфраструктуре и AI-агентах.",
    url: "https://mpeshekhonov.ru/blog",
  },
};

export default function BlogPage() {
  const posts = getBlogPosts();

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <h1 className="mb-2 text-3xl font-bold text-ink sm:text-4xl">Блог</h1>
        <p className="max-w-2xl text-ink-muted">
          Заметки о разработке, DevOps и автоматизации. Практический опыт без
          маркетинговой воды.
        </p>
      </header>

      <div className="space-y-4">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="group block rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md transition hover:border-accent/20"
          >
            <time className="font-mono text-xs text-ink-faint">
              {formatBlogDate(post.date)}
            </time>
            <h2 className="mb-2 mt-1 text-xl font-semibold text-ink group-hover:text-accent transition-colors">
              {post.title}
            </h2>
            <p className="mb-3 text-sm text-ink-muted">{post.excerpt}</p>
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-lg border border-white/6 bg-white/4 px-2.5 py-1 text-xs text-ink-muted"
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
