"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import FullChart from "@/components/FullChart";
import FundamentalsPanel from "@/components/FundamentalsPanel";
import { useDarkMode } from "@/hooks/useDarkMode";
import { api, HistoryResponse, QuoteResponse, IndicatorResponse } from "@/lib/api";

type Params = { symbol: string };

const RANGES = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"] as const;
const INTERVALS: Record<string, string> = {
  "1d": "1m",
  "5d": "5m",
  "1mo": "15m",
  "3mo": "1h",
  "6mo": "1d",
  "1y": "1d",
  "5y": "1wk",
  max: "1wk",
};

export default function TickerDetail({ params }: { params: Promise<Params> }) {
  const { symbol } = use(params);
  const ticker = decodeURIComponent(symbol);
  const { dark, toggle } = useDarkMode();

  const [range, setRange] = useState<string>("6mo");
  const [chartType, setChartType] = useState<"candle" | "line">("candle");
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(true);

  // indicator toggles
  const [showMACD, setShowMACD] = useState(false);
  const [showRSI, setShowRSI] = useState(false);
  const [showSMA, setShowSMA] = useState(false);
  const [showEMA, setShowEMA] = useState(false);

  const [macdData, setMacdData] = useState<IndicatorResponse | null>(null);
  const [rsiData, setRsiData] = useState<IndicatorResponse | null>(null);
  const [smaData, setSmaData] = useState<IndicatorResponse | null>(null);
  const [emaData, setEmaData] = useState<IndicatorResponse | null>(null);

  // Fetch history when range changes
  useEffect(() => {
    const interval = INTERVALS[range] ?? "1d";
    api.history(ticker, interval, range).then(setHistory).catch(() => setHistory(null));
  }, [ticker, range]);

  // Fetch quote once
  useEffect(() => {
    setQuoteLoading(true);
    api.quote(ticker)
      .then(setQuote)
      .catch(() => setQuote(null))
      .finally(() => setQuoteLoading(false));
  }, [ticker]);

  // Fetch indicators when toggled
  useEffect(() => {
    if (!showMACD) { setMacdData(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "macd", { interval, range }).then(setMacdData).catch(() => setMacdData(null));
  }, [showMACD, ticker, range]);

  useEffect(() => {
    if (!showRSI) { setRsiData(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "rsi", { interval, range }).then(setRsiData).catch(() => setRsiData(null));
  }, [showRSI, ticker, range]);

  useEffect(() => {
    if (!showSMA) { setSmaData(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "sma", { interval, range, period: 25 }).then(setSmaData).catch(() => setSmaData(null));
  }, [showSMA, ticker, range]);

  useEffect(() => {
    if (!showEMA) { setEmaData(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "ema", { interval, range, period: 25 }).then(setEmaData).catch(() => setEmaData(null));
  }, [showEMA, ticker, range]);

  const name = quote?.longName ?? quote?.shortName ?? ticker;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link
            href="/"
            className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            ← 一覧へ戻る
          </Link>
          <h1 className="flex-1 font-bold dark:text-white truncate">
            {name}
            <span className="ml-2 text-sm font-normal text-gray-400">{ticker}</span>
          </h1>
          <button
            onClick={toggle}
            className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-4 space-y-4">
        {/* Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Range selector */}
          <div className="flex gap-1 flex-wrap">
            {RANGES.map((r) => (
              <button
                key={r}
                onClick={() => setRange(r)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  range === r
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
          {/* Chart type */}
          <div className="flex gap-1 ml-auto">
            {(["candle", "line"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setChartType(t)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  chartType === t
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                }`}
              >
                {t === "candle" ? "🕯 ローソク" : "📈 ライン"}
              </button>
            ))}
          </div>
        </div>

        {/* Indicator toggles */}
        <div className="flex flex-wrap gap-2">
          {[
            { label: "MACD", active: showMACD, toggle: () => setShowMACD((v) => !v) },
            { label: "RSI(14)", active: showRSI, toggle: () => setShowRSI((v) => !v) },
            { label: "SMA(25)", active: showSMA, toggle: () => setShowSMA((v) => !v) },
            { label: "EMA(25)", active: showEMA, toggle: () => setShowEMA((v) => !v) },
          ].map(({ label, active, toggle }) => (
            <button
              key={label}
              onClick={toggle}
              className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
                active
                  ? "bg-indigo-600 border-indigo-600 text-white"
                  : "border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-indigo-400"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-3 overflow-hidden">
          {history && history.data.length > 0 ? (
            <FullChart
              data={history.data}
              chartType={chartType}
              dark={dark}
              macdData={macdData?.data}
              rsiData={rsiData?.data}
              smaData={smaData?.data}
              emaData={emaData?.data}
            />
          ) : (
            <div className="h-96 flex items-center justify-center text-gray-400">
              {history === null ? "読み込み中..." : "データなし"}
            </div>
          )}
        </div>

        {/* Fundamentals */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
          <h2 className="text-sm font-semibold dark:text-white mb-3">ファンダメンタル情報</h2>
          <FundamentalsPanel quote={quote} loading={quoteLoading} />
        </div>

        {/* Disclaimer */}
        <p className="text-xs text-gray-400 dark:text-gray-600">
          ※ 表示データは yfinance 経由の参考値（数十秒〜数分遅延あり）です。投資判断の根拠としないでください。
        </p>
      </main>
    </div>
  );
}
