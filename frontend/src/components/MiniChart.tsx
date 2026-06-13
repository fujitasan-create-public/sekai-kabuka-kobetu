"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, LineStyle } from "lightweight-charts";

type Props = {
  data: { t: number; c: number }[];
  positive: boolean;
  dark: boolean;
};

export default function MiniChart({ data, positive, dark: _dark }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    const color = positive ? "#22c55e" : "#ef4444";

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 60,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "transparent",
      },
      grid: { vertLines: { visible: false }, horzLines: { visible: false } },
      crosshair: { horzLine: { visible: false }, vertLine: { visible: false } },
      rightPriceScale: { visible: false },
      leftPriceScale: { visible: false },
      timeScale: { visible: false },
      handleScroll: false,
      handleScale: false,
      watermark: { visible: false },
    });

    const series = chart.addLineSeries({
      color,
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
      lastValueVisible: false,
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
  }, [data, positive]);

  return <div ref={containerRef} className="w-full h-[60px]" />;
}
