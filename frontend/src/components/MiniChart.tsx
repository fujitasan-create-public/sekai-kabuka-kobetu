"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, LineStyle } from "lightweight-charts";

type Props = {
  data: { t: number; c: number }[];
  positive: boolean;
  dark: boolean;
};

export default function MiniChart({ data, positive, dark }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    const upColor = "#22c55e";
    const downColor = "#ef4444";
    const color = positive ? upColor : downColor;
    const scaleText = dark ? "#6b7280" : "#9ca3af";
    const gridColor = dark ? "#374151" : "#e5e7eb";

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 160,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: scaleText,
        fontSize: 10,
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { color: gridColor, style: LineStyle.Dotted },
      },
      crosshair: { horzLine: { visible: false }, vertLine: { visible: false } },
      rightPriceScale: {
        visible: true,
        borderVisible: false,
        scaleMargins: { top: 0.1, bottom: 0.1 },
        ticksVisible: false,
      },
      leftPriceScale: { visible: false },
      timeScale: { visible: false, borderVisible: false },
      handleScroll: false,
      handleScale: false,
      watermark: { visible: false },
    });

    const series = chart.addLineSeries({
      color,
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
      lastValueVisible: true,
      lastPriceAnimation: 0,
    });

    series.setData(
      data.map((d) => ({ time: Math.floor(d.t / 1000) as unknown as string, value: d.c }))
    );
    chart.timeScale().fitContent();

    const ro = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    ro.observe(containerRef.current);

    return () => {
      ro.disconnect();
      chart.remove();
    };
  }, [data, positive, dark]);

  return <div ref={containerRef} className="w-full h-[160px]" />;
}
