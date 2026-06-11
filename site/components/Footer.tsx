import resume from "@/content/resume/resume.json";

export function Footer() {
  return (
    <footer className="border-t border-white/5 py-8">
      <div className="mx-auto max-w-5xl px-4 text-center text-sm text-ink-faint sm:px-6">
        © {new Date().getFullYear()} {resume.name}
      </div>
    </footer>
  );
}
