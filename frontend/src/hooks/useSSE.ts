"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

export type TickerSnapshot = {
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  intraday: { t: number; c: number }[];
  last_updated: number;
};

export function useSSE(tickers: string[]) {
  const [data, setData] = useState<Record<string, TickerSnapshot>>({});
  const esRef = useRef<EventSource | null>(null);
  const tickersKey = tickers.slice().sort().join(",");

  useEffect(() => {
    if (tickers.length === 0) return;
    if (esRef.current) {
      esRef.current.close();
    }

    const url = api.streamUrl(tickers);
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const update: Record<string, TickerSnapshot> = JSON.parse(e.data);
        setData((prev) => {
          const next = { ...prev };
          for (const [ticker, snap] of Object.entries(update)) {
            if (snap) next[ticker] = snap;
          }
          return next;
        });
      } catch {
        // ignore malformed
      }
    };

    es.onerror = () => {
      es.close();
      // retry after 10s
      setTimeout(() => {
        if (esRef.current === es) {
          esRef.current = null;
        }
      }, 10000);
    };

    return () => {
      es.close();
      esRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickersKey]);

  return data;
}
