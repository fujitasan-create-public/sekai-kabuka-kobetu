"use client";

import { useState } from "react";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import { SortableContext, rectSortingStrategy } from "@dnd-kit/sortable";
import TickerTile from "@/components/TickerTile";
import SearchModal from "@/components/SearchModal";
import { useLayout } from "@/hooks/useLayout";
import { useDarkMode } from "@/hooks/useDarkMode";
import { useSSE } from "@/hooks/useSSE";

export default function Dashboard() {
  const { tickers, add, remove, reorder } = useLayout();
  const { dark, toggle } = useDarkMode();
  const [showSearch, setShowSearch] = useState(false);

  const sseData = useSSE(tickers.map((t) => t.ticker));

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const from = tickers.findIndex((t) => t.ticker === active.id);
    const to = tickers.findIndex((t) => t.ticker === over.id);
    if (from !== -1 && to !== -1) reorder(from, to);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <h1 className="text-lg font-bold dark:text-white flex-1"> 世界の株価 個別</h1>
          <button
            onClick={() => setShowSearch(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            🔍 銘柄を追加
          </button>
          <button
            onClick={toggle}
            className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            title={dark ? "ライトモード" : "ダークモード"}
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      {/* Disclaimer */}
      <div className="max-w-7xl mx-auto px-4 py-1.5">
        <p className="text-xs text-gray-400 dark:text-gray-600">
          ※ 表示データは yfinance 経由の参考値（数十秒遅延あり）です。投資判断の根拠としないでください。
        </p>
      </div>

      {/* Grid */}
      <main className="max-w-7xl mx-auto px-4 py-4">
        {tickers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-gray-400">
            <span className="text-4xl">📊</span>
            <p>銘柄がありません。「銘柄を追加」から検索してください。</p>
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={tickers.map((t) => t.ticker)} strategy={rectSortingStrategy}>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                {tickers.map((entry) => (
                  <TickerTile
                    key={entry.ticker}
                    entry={entry}
                    snapshot={sseData[entry.ticker]}
                    dark={dark}
                    onRemove={() => remove(entry.ticker)}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}
      </main>

      {showSearch && (
        <SearchModal onAdd={add} onClose={() => setShowSearch(false)} />
      )}
    </div>
  );
}
