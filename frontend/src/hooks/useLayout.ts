"use client";

import { useEffect, useState } from "react";

export type TickerEntry = { ticker: string; name: string };

const STORAGE_KEY = "skk_layout";

const DEFAULTS: TickerEntry[] = [
  { ticker: "7203.T", name: "トヨタ自動車" },
  { ticker: "6758.T", name: "ソニーグループ" },
  { ticker: "9984.T", name: "ソフトバンクグループ" },
  { ticker: "6861.T", name: "キーエンス" },
  { ticker: "8306.T", name: "三菱UFJフィナンシャル・グループ" },
  { ticker: "9432.T", name: "日本電信電話" },
];

export function useLayout() {
  const [tickers, setTickers] = useState<TickerEntry[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      setTickers(stored ? JSON.parse(stored) : DEFAULTS);
    } catch {
      setTickers(DEFAULTS);
    }
  }, []);

  const save = (next: TickerEntry[]) => {
    setTickers(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  const add = (entry: TickerEntry) => {
    if (tickers.some((t) => t.ticker === entry.ticker)) return;
    save([...tickers, entry]);
  };

  const remove = (ticker: string) => save(tickers.filter((t) => t.ticker !== ticker));

  const reorder = (from: number, to: number) => {
    const next = [...tickers];
    const [item] = next.splice(from, 1);
    next.splice(to, 0, item);
    save(next);
  };

  return { tickers, add, remove, reorder };
}
