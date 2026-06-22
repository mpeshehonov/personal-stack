import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import type { Locale } from "@/middleware";

type Props = { className?: string; locale?: Locale };

export function SocialLinks({ className = "", locale = "ru" }: Props) {
  const resume = locale === "en" ? resumeEn : resumeRu;
  const siteLabel = locale === "en" ? "Site" : "Сайт";
  const phoneLabel = "+7 950 919-67-86";

  const socials = [
    { href: resume.links.website, label: siteLabel, icon: "WWW", external: true },
    { href: resume.links.telegram, label: "Telegram", icon: "TG", external: true },
    { href: "tel:+79509196786", label: phoneLabel, icon: "TEL", external: false },
    { href: resume.links.linkedin, label: "LinkedIn", icon: "in", external: true },
    { href: resume.links.github, label: "GitHub", icon: "GH", external: true },
  ];

  return (
    <div className={`flex flex-wrap gap-3 ${className}`}>
      {socials.map(({ href, label, icon, external }) => (
        <a
          key={href}
          href={href}
          target={external ? "_blank" : undefined}
          rel={external ? "noopener noreferrer" : undefined}
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
