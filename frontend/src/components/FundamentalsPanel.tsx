"use client";

import type { QuoteResponse } from "@/lib/api";

type Props = {
  quote: QuoteResponse | null;
  loading: boolean;
};

const fmt = (v: number | null | undefined, digits = 2) =>
  v == null ? "—" : v.toLocaleString(undefined, { maximumFractionDigits: digits });

const fmtPct = (v: number | null | undefined) =>
  v == null ? "—" : `${(v * 100).toFixed(2)}%`;

const fmtBig = (v: number | null | undefined) => {
  if (v == null) return "—";
  if (v >= 1e12) return `${(v / 1e12).toFixed(2)}兆`;
  if (v >= 1e8) return `${(v / 1e8).toFixed(2)}億`;
  return v.toLocaleString();
};

export default function FundamentalsPanel({ quote, loading }: Props) {
  if (loading) return <div className="text-gray-400 text-sm py-4">読み込み中...</div>;
  if (!quote) return null;

  const rows = [
    { label: "PER（実績）", value: fmt(quote.trailingPE) },
    { label: "PER（予想）", value: fmt(quote.forwardPE) },
    { label: "PBR", value: fmt(quote.priceToBook) },
    { label: "EPS", value: fmt(quote.trailingEps) },
    { label: "時価総額", value: fmtBig(quote.marketCap) },
    { label: "配当利回り", value: fmtPct(quote.dividendYield) },
    { label: "52週高値", value: fmt(quote.fiftyTwoWeekHigh) },
    { label: "52週安値", value: fmt(quote.fiftyTwoWeekLow) },
    { label: "出来高", value: fmtBig(quote.volume) },
    { label: "平均出来高", value: fmtBig(quote.averageVolume) },
    { label: "ベータ", value: fmt(quote.beta) },
    { label: "セクター", value: quote.sector ?? "—" },
    { label: "業種", value: quote.industry ?? "—" },
    { label: "通貨", value: quote.currency ?? "—" },
    { label: "取引所", value: quote.exchange ?? "—" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-2">
      {rows.map((r) => (
        <div key={r.label} className="flex flex-col">
          <span className="text-xs text-gray-400 dark:text-gray-500">{r.label}</span>
          <span className="text-sm font-medium dark:text-white">{r.value}</span>
        </div>
      ))}
    </div>
  );
}
