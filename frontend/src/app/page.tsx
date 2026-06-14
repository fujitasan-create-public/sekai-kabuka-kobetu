"use client";

import { useState } from "react";
import Image from "next/image";
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

  const { data: sseData, loading: sseLoading } = useSSE(tickers.map((t) => t.ticker));

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const from = tickers.findIndex((t) => t.ticker === active.id);
    const to = tickers.findIndex((t) => t.ticker === over.id);
    if (from !== -1 && to !== -1) reorder(from, to);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="w-full px-3 py-2 flex items-center gap-3">
          <h1 className="text-sm font-bold dark:text-white flex-1">世界の株価 個別</h1>
          <p className="text-[10px] text-gray-400 dark:text-gray-600 hidden sm:block">
            ※ 参考値につき投資判断の根拠としないでください。一部のグロース株は表示されない場合があります。
          </p>
          <button
            onClick={() => setShowSearch(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors whitespace-nowrap"
          >
            <Image src="/search.png" alt="検索" width={16} height={16} /> 銘柄を追加
          </button>
          <button
            onClick={toggle}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            title={dark ? "ライトモード" : "ダークモード"}
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      {/* Grid — full width, no max-width */}
      <main className="w-full p-1">
        {tickers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-gray-400">
            <span className="text-4xl">📊</span>
            <p>銘柄がありません。「銘柄を追加」から検索してください。</p>
          </div>
        ) : sseLoading ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-gray-400 dark:text-gray-500">
            <div className="animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent" />
            <p className="text-sm">データを読み込み中...(時間がかかる場合があります。少々お待ちください)</p>
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={tickers.map((t) => t.ticker)} strategy={rectSortingStrategy}>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1">
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
