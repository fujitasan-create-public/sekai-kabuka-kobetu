"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { api, TickerSummary } from "@/lib/api";
import type { TickerEntry } from "@/hooks/useLayout";

type Props = {
  onAdd: (entry: TickerEntry) => void;
  onClose: () => void;
};

export default function SearchModal({ onAdd, onClose }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<TickerSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (!query.trim()) { setResults([]); return; }
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await api.search(query.trim());
        setResults(res);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, [query]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/50"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg bg-white dark:bg-gray-900 rounded-xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <Image src="/search.png" alt="検索" width={16} height={16} className="opacity-40" />
          <input
            ref={inputRef}
            className="flex-1 bg-transparent outline-none dark:text-white placeholder-gray-400"
            placeholder="銘柄コードまたは銘柄名で検索..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKey}
          />
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">✕</button>
        </div>
        <div className="max-h-80 overflow-y-auto">
          {loading && (
            <div className="p-4 text-center text-gray-400 text-sm">検索中...</div>
          )}
          {!loading && query && results.length === 0 && (
            <div className="p-4 text-center text-gray-400 text-sm">見つかりませんでした</div>
          )}
          {results.map((r) => (
            <button
              key={r.ticker}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 text-left"
              onClick={() => { onAdd({ ticker: r.ticker, name: r.name }); onClose(); }}
            >
              <span className="font-mono text-sm text-gray-500 w-24 shrink-0">{r.ticker}</span>
              <span className="text-sm dark:text-white truncate">{r.name}</span>
              <span className="text-xs text-gray-400 ml-auto">{r.market}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
