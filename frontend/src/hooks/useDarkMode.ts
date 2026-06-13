"use client";

import { useEffect, useState } from "react";

const KEY = "skk_dark";

export function useDarkMode() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(KEY);
    const initial = stored ? stored === "1" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDark(initial);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem(KEY, dark ? "1" : "0");
  }, [dark]);

  return { dark, toggle: () => setDark((d) => !d) };
}
