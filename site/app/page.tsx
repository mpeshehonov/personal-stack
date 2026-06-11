import Link from "next/link";
import resume from "@/content/resume/resume.json";

export default function HomePage() {
  return (
    <div className="hero">
      <h1>{resume.name}</h1>
      <p>{resume.title}</p>
      <div className="card">
        <p>{resume.summary}</p>
        <Link href="/resume" className="btn">
          Резюме
        </Link>
      </div>
    </div>
  );
}
