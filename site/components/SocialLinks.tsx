import resume from "@/content/resume/resume.json";

const socials = [
  { href: resume.links.telegram, label: "Telegram", icon: "TG" },
  { href: resume.links.linkedin, label: "LinkedIn", icon: "in" },
  { href: resume.links.github, label: "GitHub", icon: "GH" },
];

type Props = { className?: string };

export function SocialLinks({ className = "" }: Props) {
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
