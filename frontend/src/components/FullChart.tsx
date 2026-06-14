"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, LineStyle, TickMarkType } from "lightweight-charts";
import type { OHLCVBar, IndicatorDataPoint } from "@/lib/api";

type Props = {
  data: OHLCVBar[];
  chartType: "candle" | "line";
  dark: boolean;
  sma5Data?: IndicatorDataPoint[];
  sma25Data?: IndicatorDataPoint[];
  sma75Data?: IndicatorDataPoint[];
  bbData?: IndicatorDataPoint[];
  macdData?: IndicatorDataPoint[];
  rsiData?: IndicatorDataPoint[];
  showVolume?: boolean;
};

export default function FullChart({
  data, chartType, dark,
  sma5Data, sma25Data, sma75Data, bbData,
  macdData, rsiData, showVolume,
}: Props) {
  const mainRef = useRef<HTMLDivElement>(null);
  const macdRef = useRef<HTMLDivElement>(null);
  const rsiRef  = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mainRef.current || data.length === 0) return;

    const bg          = dark ? "#111827" : "#ffffff";
    const textColor   = dark ? "#9ca3af" : "#374151";
    const gridColor   = dark ? "#1f2937" : "#f3f4f6";
    const borderColor = dark ? "#374151" : "#e5e7eb";

    const toJST = (utcSec: number) => new Date((utcSec + 9 * 3600) * 1000);

    const chartOpts = {
      layout: { background: { type: ColorType.Solid, color: bg }, textColor },
      grid: { vertLines: { color: gridColor }, horzLines: { color: gridColor } },
      localization: {
        timeFormatter: (time: number) => {
          const jst = toJST(time);
          const mo = jst.getUTCMonth() + 1;
          const d  = jst.getUTCDate();
          const h  = String(jst.getUTCHours()).padStart(2, "0");
          const m  = String(jst.getUTCMinutes()).padStart(2, "0");
          return `${mo}/${d} ${h}:${m}`;
        },
      },
      timeScale: {
        borderColor,
        timeVisible: true,
        secondsVisible: false,
        tickMarkFormatter: (time: number, markType: TickMarkType) => {
          const jst = toJST(time);
          switch (markType) {
            case TickMarkType.Time:
            case TickMarkType.TimeWithSeconds:
              return `${String(jst.getUTCHours()).padStart(2, "0")}:${String(jst.getUTCMinutes()).padStart(2, "0")}`;
            case TickMarkType.DayOfMonth:
              return `${jst.getUTCMonth() + 1}/${jst.getUTCDate()}`;
            case TickMarkType.Month:
              return `${jst.getUTCFullYear()}/${jst.getUTCMonth() + 1}`;
            default:
              return String(jst.getUTCFullYear());
          }
        },
      },
      rightPriceScale: { borderColor },
      watermark: { visible: false },
    };

    const mainChart = createChart(mainRef.current, {
      ...chartOpts,
      width: mainRef.current.clientWidth,
      height: 380,
    });

    const toTime = (ms: number) => Math.floor(ms / 1000) as unknown as string;

    // ── メインシリーズ ──────────────────────────────────────────
    if (chartType === "candle") {
      const series = mainChart.addCandlestickSeries({
        upColor: "#22c55e", downColor: "#ef4444",
        borderVisible: false,
        wickUpColor: "#22c55e", wickDownColor: "#ef4444",
      });
      series.setData(
        data.map((d) =>
          d.o !== null && d.h !== null && d.l !== null && d.c !== null
            ? { time: toTime(d.t), open: d.o, high: d.h, low: d.l, close: d.c }
            : { time: toTime(d.t) }
        ) as Parameters<typeof series.setData>[0]
      );
    } else {
      // lightweight-charts の line シリーズは whitespace（値なし点）を飛び越えて
      // 線を直結してしまうため、null 行を境に連続区間ごとへ分割し、区間ごとに
      // 別々の line シリーズを描くことで昼休み等のギャップを表現する。
      type LinePoint = { time: ReturnType<typeof toTime>; value: number };
      const segments: LinePoint[][] = [];
      let current: LinePoint[] = [];
      const gapPoints: { time: ReturnType<typeof toTime> }[] = [];

      for (const d of data) {
        const hasValue = d.o !== null && d.h !== null && d.l !== null && d.c !== null;
        if (hasValue) {
          current.push({ time: toTime(d.t), value: d.c! });
        } else {
          // 欠損行（昼休み等）。区間を区切りつつ、時間軸スロットは確保しておく。
          if (current.length > 0) {
            segments.push(current);
            current = [];
          }
          gapPoints.push({ time: toTime(d.t) });
        }
      }
      if (current.length > 0) segments.push(current);

      // 欠損時間帯を whitespace として時間軸へ供給（candle と同じ空白幅を保つ）。
      if (gapPoints.length > 0) {
        const spacer = mainChart.addLineSeries({ lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false });
        spacer.setData(gapPoints as Parameters<typeof spacer.setData>[0]);
      }

      segments.forEach((seg, idx) => {
        const series = mainChart.addLineSeries({
          color: "#6366f1",
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: idx === segments.length - 1,
        });
        series.setData(seg as Parameters<typeof series.setData>[0]);
      });
    }

    // ── 出来高 ────────────────────────────────────────────────
    if (showVolume) {
      const volSeries = mainChart.addHistogramSeries({
        color: "#22c55e",
        priceFormat: { type: "volume" },
        priceScaleId: "volume",
      } as Parameters<typeof mainChart.addHistogramSeries>[0]);
      volSeries.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
      volSeries.setData(
        data
          .filter((d) => d.v != null)
          .map((d) => ({
            time: toTime(d.t),
            value: d.v!,
            color: d.c != null && d.o != null && d.c >= d.o ? "#22c55e88" : "#ef444488",
          })) as Parameters<typeof volSeries.setData>[0]
      );
    }

    // ── 移動平均線 ──────────────────────────────────────────────
    const addSMA = (pts: IndicatorDataPoint[], color: string) => {
      const s = mainChart.addLineSeries({ color, lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      s.setData(pts.filter((d) => d.v != null).map((d) => ({ time: toTime(d.t), value: d.v! })));
    };
    if (sma5Data  && sma5Data.length  > 0) addSMA(sma5Data,  "#3b82f6");
    if (sma25Data && sma25Data.length > 0) addSMA(sma25Data, "#f59e0b");
    if (sma75Data && sma75Data.length > 0) addSMA(sma75Data, "#ef4444");

    // ── ボリンジャーバンド ──────────────────────────────────────
    if (bbData && bbData.length > 0) {
      const bbColor = dark ? "#94a3b8" : "#64748b";
      const addBBLine = (getter: (d: IndicatorDataPoint) => number | null | undefined, style: LineStyle) => {
        const s = mainChart.addLineSeries({ color: bbColor, lineWidth: 1, lineStyle: style, priceLineVisible: false, lastValueVisible: false });
        s.setData(bbData.filter((d) => getter(d) != null).map((d) => ({ time: toTime(d.t), value: getter(d)! })));
      };
      addBBLine((d) => d.upper,  LineStyle.Dashed);
      addBBLine((d) => d.middle, LineStyle.Solid);
      addBBLine((d) => d.lower,  LineStyle.Dashed);
    }

    mainChart.timeScale().fitContent();

    // ── MACD パネル ────────────────────────────────────────────
    let macdChart: ReturnType<typeof createChart> | null = null;
    if (macdData && macdData.length > 0 && macdRef.current) {
      macdChart = createChart(macdRef.current, { ...chartOpts, width: macdRef.current.clientWidth, height: 120 });
      const macdLine   = macdChart.addLineSeries({ color: "#6366f1", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      const signalLine = macdChart.addLineSeries({ color: "#f59e0b", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      const histSeries = macdChart.addHistogramSeries({ priceLineVisible: false, lastValueVisible: false } as Parameters<typeof macdChart.addHistogramSeries>[0]);
      macdLine.setData(macdData.filter((d) => d.macd != null).map((d) => ({ time: toTime(d.t), value: d.macd! })));
      signalLine.setData(macdData.filter((d) => d.signal != null).map((d) => ({ time: toTime(d.t), value: d.signal! })));
      histSeries.setData(macdData.filter((d) => d.histogram != null).map((d) => ({ time: toTime(d.t), value: d.histogram!, color: d.histogram! >= 0 ? "#22c55e" : "#ef4444" })));
      macdChart.timeScale().fitContent();
    }

    // ── RSI パネル ─────────────────────────────────────────────
    let rsiChart: ReturnType<typeof createChart> | null = null;
    if (rsiData && rsiData.length > 0 && rsiRef.current) {
      rsiChart = createChart(rsiRef.current, { ...chartOpts, width: rsiRef.current.clientWidth, height: 100 });
      const rsiLine = rsiChart.addLineSeries({ color: "#22d3ee", lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      rsiLine.setData(rsiData.filter((d) => d.v != null).map((d) => ({ time: toTime(d.t), value: d.v! })));
      rsiChart.timeScale().fitContent();
    }

    const ro = new ResizeObserver(() => {
      if (mainRef.current)  mainChart.applyOptions({ width: mainRef.current.clientWidth });
      if (macdRef.current && macdChart) macdChart.applyOptions({ width: macdRef.current.clientWidth });
      if (rsiRef.current  && rsiChart)  rsiChart.applyOptions({ width: rsiRef.current.clientWidth });
    });
    ro.observe(mainRef.current);

    return () => {
      ro.disconnect();
      mainChart.remove();
      macdChart?.remove();
      rsiChart?.remove();
    };
  }, [data, chartType, dark, sma5Data, sma25Data, sma75Data, bbData, macdData, rsiData, showVolume]);

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
