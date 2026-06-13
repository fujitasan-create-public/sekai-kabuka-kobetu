"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import Link from "next/link";
import MiniChart from "./MiniChart";
import type { TickerSnapshot } from "@/hooks/useSSE";
import type { TickerEntry } from "@/hooks/useLayout";

type Props = {
  entry: TickerEntry;
  snapshot: TickerSnapshot | undefined;
  dark: boolean;
  onRemove: () => void;
};

export default function TickerTile({ entry, snapshot, dark, onRemove }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: entry.ticker,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const positive = !snapshot || snapshot.change_pct >= 0;
  const pctColor = positive ? "text-green-500" : "text-red-500";
  const pctBg   = positive ? "bg-green-50 dark:bg-green-950" : "bg-red-50 dark:bg-red-950";
  const pct = snapshot
    ? `${snapshot.change_pct >= 0 ? "+" : ""}${snapshot.change_pct.toFixed(2)}%`
    : "---";
  const chg = snapshot
    ? `${snapshot.change >= 0 ? "+" : ""}${snapshot.change.toFixed(2)}`
    : "---";
  const price = snapshot
    ? snapshot.price.toLocaleString("ja-JP", { maximumFractionDigits: 2 })
    : "---";

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`relative group rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden ${pctBg}`}
    >
      {/* drag handle */}
      <div
        {...listeners}
        {...attributes}
        className="absolute top-2 right-8 z-10 w-5 h-5 flex items-center justify-center text-gray-400 cursor-grab opacity-0 group-hover:opacity-100 transition-opacity select-none"
        title="ドラッグで並び替え"
      >
        ⠿
      </div>
      {/* remove */}
      <button
        onClick={(e) => { e.stopPropagation(); onRemove(); }}
        className="absolute top-1.5 right-2 z-10 w-5 h-5 flex items-center justify-center text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-xs"
        title="削除"
      >
        ✕
      </button>

      <Link href={`/ticker/${encodeURIComponent(entry.ticker)}`} className="block p-3">
        {/* Header: name + ticker */}
        <div className="flex items-start justify-between mb-1">
          <div className="min-w-0">
            <div className="text-xs font-medium text-gray-700 dark:text-gray-200 truncate leading-tight">
              {entry.name}
            </div>
            <div className="text-[10px] text-gray-400 dark:text-gray-500 font-mono">
              {entry.ticker}
            </div>
          </div>
          {/* % change badge */}
          <div className={`ml-2 text-xl font-bold leading-none ${pctColor} whitespace-nowrap`}>
            {pct}
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white dark:bg-gray-800 rounded overflow-hidden -mx-1">
          <MiniChart
            data={snapshot?.intraday ?? []}
            positive={positive}
            dark={dark}
          />
        </div>

        {/* Footer: price + change */}
        <div className="flex items-baseline justify-between mt-1.5">
          <span className="text-base font-bold dark:text-white tabular-nums">
            {price}
          </span>
          <span className={`text-xs font-medium tabular-nums ${pctColor}`}>
            {chg}
          </span>
        </div>
      </Link>
    </div>
  );
}
