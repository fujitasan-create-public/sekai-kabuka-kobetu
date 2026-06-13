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
    opacity: isDragging ? 0.5 : 1,
  };

  const positive = !snapshot || snapshot.change >= 0;
  const changeColor = positive ? "text-green-500" : "text-red-500";
  const pct = snapshot ? snapshot.change_pct.toFixed(2) : "---";
  const chg = snapshot ? (snapshot.change >= 0 ? "+" : "") + snapshot.change.toFixed(2) : "---";
  const price = snapshot ? snapshot.price.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "---";

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="relative group rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
    >
      {/* drag handle */}
      <div
        {...listeners}
        {...attributes}
        className="absolute top-2 right-8 w-5 h-5 flex items-center justify-center text-gray-400 cursor-grab opacity-0 group-hover:opacity-100 transition-opacity"
        title="ドラッグで並び替え"
      >
        ⠿
      </div>
      {/* remove */}
      <button
        onClick={(e) => { e.stopPropagation(); onRemove(); }}
        className="absolute top-2 right-2 w-5 h-5 flex items-center justify-center text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity text-xs"
        title="削除"
      >
        ✕
      </button>

      <Link href={`/ticker/${encodeURIComponent(entry.ticker)}`} className="block">
        <div className="flex justify-between items-start mb-1">
          <div>
            <div className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[120px]">{entry.name}</div>
            <div className="text-xs font-mono text-gray-400 dark:text-gray-500">{entry.ticker}</div>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold dark:text-white">{price}</div>
            <div className={`text-xs font-medium ${changeColor}`}>
              {chg} ({pct}%)
            </div>
          </div>
        </div>
        <MiniChart
          data={snapshot?.intraday ?? []}
          positive={positive}
          dark={dark}
        />
      </Link>
    </div>
  );
}
