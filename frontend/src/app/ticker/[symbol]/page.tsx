"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import FullChart from "@/components/FullChart";
import FundamentalsPanel from "@/components/FundamentalsPanel";
import { useDarkMode } from "@/hooks/useDarkMode";
import { api, HistoryResponse, QuoteResponse, IndicatorResponse, FilingsResponse } from "@/lib/api";

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

  const [showSMA5, setShowSMA5] = useState(false);
  const [showSMA25, setShowSMA25] = useState(false);
  const [showSMA75, setShowSMA75] = useState(false);
  const [showBB, setShowBB] = useState(false);
  const [showMACD, setShowMACD] = useState(false);
  const [showRSI, setShowRSI] = useState(false);
  const [showVolume, setShowVolume] = useState(false);

  const [sma5Data, setSma5Data] = useState<IndicatorResponse | null>(null);
  const [sma25Data, setSma25Data] = useState<IndicatorResponse | null>(null);
  const [sma75Data, setSma75Data] = useState<IndicatorResponse | null>(null);
  const [bbData, setBbData] = useState<IndicatorResponse | null>(null);
  const [macdData, setMacdData] = useState<IndicatorResponse | null>(null);
  const [rsiData, setRsiData] = useState<IndicatorResponse | null>(null);
  const [filings, setFilings] = useState<FilingsResponse | null>(null);

  useEffect(() => {
    const interval = INTERVALS[range] ?? "1d";
    api.history(ticker, interval, range).then(setHistory).catch(() => setHistory(null));
  }, [ticker, range]);

  useEffect(() => {
    api.filings(ticker).then(setFilings).catch(() => setFilings(null));
  }, [ticker]);

  useEffect(() => {
    setQuoteLoading(true);
    api.quote(ticker)
      .then(setQuote)
      .catch(() => setQuote(null))
      .finally(() => setQuoteLoading(false));
  }, [ticker]);

  useEffect(() => {
    if (!showSMA5) { setSma5Data(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "sma", { interval, range, period: 5 }).then(setSma5Data).catch(() => setSma5Data(null));
  }, [showSMA5, ticker, range]);

  useEffect(() => {
    if (!showSMA25) { setSma25Data(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "sma", { interval, range, period: 25 }).then(setSma25Data).catch(() => setSma25Data(null));
  }, [showSMA25, ticker, range]);

  useEffect(() => {
    if (!showSMA75) { setSma75Data(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "sma", { interval, range, period: 75 }).then(setSma75Data).catch(() => setSma75Data(null));
  }, [showSMA75, ticker, range]);

  useEffect(() => {
    if (!showBB) { setBbData(null); return; }
    const interval = INTERVALS[range] ?? "1d";
    api.indicators(ticker, "bb", { interval, range, period: 20 }).then(setBbData).catch(() => setBbData(null));
  }, [showBB, ticker, range]);

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

  const name = quote?.longName ?? quote?.shortName ?? ticker;

  const indicatorButtons = [
    { label: "SMA 5",   active: showSMA5,   toggle: () => setShowSMA5((v) => !v) },
    { label: "SMA 25",  active: showSMA25,  toggle: () => setShowSMA25((v) => !v) },
    { label: "SMA 75",  active: showSMA75,  toggle: () => setShowSMA75((v) => !v) },
    { label: "BB(20)",  active: showBB,     toggle: () => setShowBB((v) => !v) },
    { label: "MACD",    active: showMACD,   toggle: () => setShowMACD((v) => !v) },
    { label: "RSI(14)", active: showRSI,    toggle: () => setShowRSI((v) => !v) },
    { label: "出来高",   active: showVolume, toggle: () => setShowVolume((v) => !v) },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
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
        <div className="flex flex-wrap items-center gap-2">
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
                {t === "candle" ? "ローソク足" : "線"}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {indicatorButtons.map(({ label, active, toggle }) => (
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

        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-3 overflow-hidden">
          {history && history.data.length > 0 ? (
            <FullChart
              data={history.data}
              chartType={chartType}
              dark={dark}
              sma5Data={sma5Data?.data}
              sma25Data={sma25Data?.data}
              sma75Data={sma75Data?.data}
              bbData={bbData?.data}
              macdData={macdData?.data}
              rsiData={rsiData?.data}
              showVolume={showVolume}
            />
          ) : (
            <div className="h-96 flex items-center justify-center text-gray-400">
              {history === null ? "読み込み中..." : "データなし"}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
          <h2 className="text-sm font-semibold dark:text-white mb-3">ファンダメンタル情報</h2>
          <FundamentalsPanel quote={quote} loading={quoteLoading} />
        </div>

        {/* 決算資料 */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold dark:text-white">決算資料</h2>
            <div className="flex gap-3">
              {filings?.tdnet_url && (
                <a href={filings.tdnet_url} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-emerald-500 hover:text-emerald-400">
                  TDnet →
                </a>
              )}
              {filings?.search_url && (
                <a href={filings.search_url} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-indigo-500 hover:text-indigo-400">
                  {filings.source === "edinet" ? "EDINET →" : "SEC EDGAR →"}
                </a>
              )}
            </div>
          </div>

          {filings === null ? (
            <p className="text-xs text-gray-400">読み込み中...</p>
          ) : filings.filings.length === 0 ? (
            <p className="text-xs text-gray-400">
              {filings.source === "edinet" && !filings.has_key
                ? "EDINET API キーが未設定です。EDINET で手動検索してください。"
                : "直近の開示書類が見つかりませんでした。"}
              {filings.search_url && (
                <a
                  href={filings.search_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-2 text-indigo-500 hover:text-indigo-400 underline"
                >
                  {filings.source === "edinet" ? "EDINET を開く" : "SEC EDGAR を開く"}
                </a>
              )}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-gray-400 dark:text-gray-500 border-b border-gray-100 dark:border-gray-800">
                    <th className="pb-1 pr-4 font-medium">種類</th>
                    <th className="pb-1 pr-4 font-medium">提出日</th>
                    <th className="pb-1 font-medium">書類名</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                  {filings.filings.map((f, i) => (
                    <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <td className="py-1.5 pr-4 whitespace-nowrap">
                        <span className={`font-mono text-xs ${
                          f.source === "tdnet"
                            ? "text-emerald-600 dark:text-emerald-400"
                            : "text-indigo-600 dark:text-indigo-400"
                        }`}>
                          {f.form}
                        </span>
                        {f.source === "tdnet" && (
                          <span className="ml-1 text-[10px] text-emerald-500 dark:text-emerald-500">TDnet</span>
                        )}
                      </td>
                      <td className="py-1.5 pr-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                        {f.date}
                      </td>
                      <td className="py-1.5">
                        <a
                          href={f.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline"
                        >
                          {f.description}
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-600">
          ※ 表示データは参考値です。投資判断の根拠としないでください。
        </p>
      </main>
    </div>
  );
}
