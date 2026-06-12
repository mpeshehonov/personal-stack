import fs from "fs";
import path from "path";
import postsManifest from "@/content/blog/posts.json";

export type BlogPostMeta = {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  tags: string[];
  draft?: boolean;
};

export type BlogPost = BlogPostMeta & {
  content: string;
};

const blogDir = path.join(process.cwd(), "content/blog");

export function getBlogPosts(): BlogPostMeta[] {
  return (postsManifest as BlogPostMeta[])
    .filter((p) => !p.draft)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export function getBlogPostBySlug(slug: string): BlogPost | undefined {
  const meta = (postsManifest as BlogPostMeta[]).find((p) => p.slug === slug);
  if (!meta) return undefined;

  const filePath = path.join(blogDir, `${slug}.md`);
  if (!fs.existsSync(filePath)) return undefined;

  const content = fs.readFileSync(filePath, "utf-8");
  return { ...meta, content };
}

export function getAllBlogSlugs(): string[] {
  return getBlogPosts().map((p) => p.slug);
}

export function formatBlogDate(date: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(date));
}
