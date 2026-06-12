import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  formatBlogDate,
  getAllBlogSlugs,
  getBlogPostBySlug,
} from "@/lib/blog";

type Props = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return getAllBlogSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = getBlogPostBySlug(slug);
  if (!post) return {};

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      url: `https://mpeshekhonov.ru/blog/${slug}`,
      type: "article",
      publishedTime: post.date,
    },
  };
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getBlogPostBySlug(slug);
  if (!post) notFound();

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <Link
          href="/blog"
          className="mb-4 inline-block text-sm text-ink-faint hover:text-accent"
        >
          ← Все записи
        </Link>
        <time className="font-mono text-xs text-ink-faint">
          {formatBlogDate(post.date)}
        </time>
        <h1 className="mb-4 mt-2 text-3xl font-bold text-ink sm:text-4xl">
          {post.title}
        </h1>
        <div className="flex flex-wrap gap-2">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-lg border border-accent/20 bg-accent/8 px-2.5 py-1 text-xs text-accent"
            >
              {tag}
            </span>
          ))}
        </div>
      </header>

      <div className="prose-blog rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md sm:p-8">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
