import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import type { Locale } from "@/middleware";

type Props = { className?: string; locale?: Locale };

export function SocialLinks({ className = "", locale = "ru" }: Props) {
  const resume = locale === "en" ? resumeEn : resumeRu;
  const siteLabel = locale === "en" ? "Site" : "Сайт";

  const socials = [
    { href: resume.links.website, label: siteLabel, icon: "WWW" },
    { href: resume.links.telegram, label: "Telegram", icon: "TG" },
    { href: resume.links.linkedin, label: "LinkedIn", icon: "in" },
    { href: resume.links.github, label: "GitHub", icon: "GH" },
  ];

  return (
    <div className={`flex flex-wrap gap-3 ${className}`}>
      {socials.map(({ href, label, icon }) => (
        <a
          key={href}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-ink-muted backdrop-blur-sm transition-all hover:border-accent/30 hover:bg-accent/5 hover:text-accent"
        >
          <span className="font-mono text-xs font-bold text-accent/80 group-hover:text-accent">
            {icon}
          </span>
          {label}
        </a>
      ))}
    </div>
  );
}
