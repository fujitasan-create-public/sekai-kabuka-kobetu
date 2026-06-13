"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType } from "lightweight-charts";
import type { OHLCVBar, IndicatorDataPoint } from "@/lib/api";

type Props = {
  data: OHLCVBar[];
  chartType: "candle" | "line";
  dark: boolean;
  macdData?: IndicatorDataPoint[];
  rsiData?: IndicatorDataPoint[];
  smaData?: IndicatorDataPoint[];
  emaData?: IndicatorDataPoint[];
};

export default function FullChart({ data, chartType, dark, macdData, rsiData, smaData, emaData }: Props) {
  const mainRef = useRef<HTMLDivElement>(null);
  const macdRef = useRef<HTMLDivElement>(null);
  const rsiRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mainRef.current || data.length === 0) return;

    const bg = dark ? "#111827" : "#ffffff";
    const textColor = dark ? "#9ca3af" : "#374151";
    const gridColor = dark ? "#1f2937" : "#f3f4f6";
    const borderColor = dark ? "#374151" : "#e5e7eb";

    const chartOpts = {
      layout: { background: { type: ColorType.Solid, color: bg }, textColor },
      grid: { vertLines: { color: gridColor }, horzLines: { color: gridColor } },
      timeScale: { borderColor },
      rightPriceScale: { borderColor },
    };

    const mainChart = createChart(mainRef.current, {
      ...chartOpts,
      width: mainRef.current.clientWidth,
      height: 380,
    });

    const validData = data.filter((d) => d.o !== null && d.h !== null && d.l !== null && d.c !== null);

    if (chartType === "candle") {
      const series = mainChart.addCandlestickSeries({
        upColor: "#22c55e",
        downColor: "#ef4444",
        borderVisible: false,
        wickUpColor: "#22c55e",
        wickDownColor: "#ef4444",
      });
      series.setData(
        validData.map((d) => ({
          time: Math.floor(d.t / 1000) as unknown as string,
          open: d.o!,
          high: d.h!,
          low: d.l!,
          close: d.c!,
        }))
      );
    } else {
      const series = mainChart.addLineSeries({ color: "#6366f1", lineWidth: 2, priceLineVisible: false });
      series.setData(
        validData.map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.c! }))
      );
    }

    if (smaData && smaData.length > 0) {
      const smaSeries = mainChart.addLineSeries({ color: "#f59e0b", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      smaSeries.setData(smaData.filter((d) => d.v != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.v! })));
    }

    if (emaData && emaData.length > 0) {
      const emaSeries = mainChart.addLineSeries({ color: "#8b5cf6", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      emaSeries.setData(emaData.filter((d) => d.v != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.v! })));
    }

    mainChart.timeScale().fitContent();

    let macdChart: ReturnType<typeof createChart> | null = null;
    if (macdData && macdData.length > 0 && macdRef.current) {
      macdChart = createChart(macdRef.current, { ...chartOpts, width: macdRef.current.clientWidth, height: 120 });
      const macdLine = macdChart.addLineSeries({ color: "#6366f1", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      const signalLine = macdChart.addLineSeries({ color: "#f59e0b", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      const histSeries = macdChart.addHistogramSeries({ priceLineVisible: false, lastValueVisible: false } as Parameters<typeof macdChart.addHistogramSeries>[0]);
      macdLine.setData(macdData.filter((d) => d.macd != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.macd! })));
      signalLine.setData(macdData.filter((d) => d.signal != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.signal! })));
      histSeries.setData(macdData.filter((d) => d.histogram != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.histogram!, color: d.histogram! >= 0 ? "#22c55e" : "#ef4444" })));
      macdChart.timeScale().fitContent();
    }

    let rsiChart: ReturnType<typeof createChart> | null = null;
    if (rsiData && rsiData.length > 0 && rsiRef.current) {
      rsiChart = createChart(rsiRef.current, { ...chartOpts, width: rsiRef.current.clientWidth, height: 100 });
      const rsiLine = rsiChart.addLineSeries({ color: "#22d3ee", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      rsiLine.setData(rsiData.filter((d) => d.v != null).map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.v! })));
      rsiChart.timeScale().fitContent();
    }

    const ro = new ResizeObserver(() => {
      if (mainRef.current) mainChart.applyOptions({ width: mainRef.current.clientWidth });
      if (macdRef.current && macdChart) macdChart.applyOptions({ width: macdRef.current.clientWidth });
      if (rsiRef.current && rsiChart) rsiChart.applyOptions({ width: rsiRef.current.clientWidth });
    });
    ro.observe(mainRef.current);

    return () => {
      ro.disconnect();
      mainChart.remove();
      macdChart?.remove();
      rsiChart?.remove();
    };
  }, [data, chartType, dark, macdData, rsiData, smaData, emaData]);

  return (
    <div className="w-full">
      <div ref={mainRef} className="w-full" />
      {macdData && macdData.length > 0 && (
        <div>
          <div className="text-xs text-gray-400 dark:text-gray-500 px-1 mt-2">MACD</div>
          <div ref={macdRef} className="w-full" />
        </div>
      )}
      {rsiData && rsiData.length > 0 && (
        <div>
          <div className="text-xs text-gray-400 dark:text-gray-500 px-1 mt-2">RSI</div>
          <div ref={rsiRef} className="w-full" />
        </div>
      )}
    </div>
  );
}
