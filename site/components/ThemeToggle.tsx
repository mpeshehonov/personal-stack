"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "theme";

export function ThemeToggle({ className = "" }: { className?: string }) {
  const [dark, setDark] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const initialDark = stored === "dark";
    document.documentElement.classList.toggle("dark", initialDark);
    setDark(initialDark);
    setReady(true);
  }, []);

  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem(STORAGE_KEY, next ? "dark" : "light");
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className={className}
      aria-label={dark ? "Light theme" : "Dark theme"}
      title={dark ? "Light theme" : "Dark theme"}
      disabled={!ready}
    >
      <span aria-hidden>{dark ? "☀" : "☾"}</span>
    </button>
  );
}
