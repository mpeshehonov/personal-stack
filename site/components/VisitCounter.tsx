"use client";

import { useEffect, useState } from "react";

type Props = {
  label: string;
};

const SESSION_KEY = "visit-recorded";

export function VisitCounter({ label }: Props) {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    const loadCount = () =>
      fetch("/api/visit")
        .then((r) => r.json())
        .then((d: { count?: number }) => setCount(d.count ?? 0))
        .catch(() => {});

    if (sessionStorage.getItem(SESSION_KEY)) {
      loadCount();
      return;
    }

    fetch("/api/visit", { method: "POST" })
      .then((r) => r.json())
      .then((d: { count?: number }) => {
        sessionStorage.setItem(SESSION_KEY, "1");
        setCount(d.count ?? 0);
      })
      .catch(loadCount);
  }, []);

  if (count === null) return null;

  return (
    <p className="font-mono text-xs text-ink-faint" aria-label={`${label}: ${count}`}>
      {label}: {count.toLocaleString()}
    </p>
  );
}
