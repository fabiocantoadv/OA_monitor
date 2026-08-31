import { useEffect, useRef } from "react";

interface VegaChartProps {
  spec: Record<string, unknown>;
  onViewReady?: (view: { toImageURL: (type: "png" | "svg") => Promise<string> } | null) => void;
}

export function VegaChart({ spec, onViewReady }: VegaChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let canceled = false;
    let view: { finalize: () => void } | null = null;

    async function renderChart() {
      if (!containerRef.current) return;

      const vega = await import("vega");
      const runtime = vega.parse(spec);

      view = new vega.View(runtime, {
        renderer: "canvas",
        container: containerRef.current,
        hover: true,
      });

      await view.runAsync();
      onViewReady?.(view as unknown as { toImageURL: (type: "png" | "svg") => Promise<string> });

      if (canceled) {
        view.finalize();
        onViewReady?.(null);
        return;
      }
    }

    renderChart().catch((error) => {
      console.error("Erro ao renderizar gráfico Vega:", error);
    });

    return () => {
      canceled = true;
      if (view) view.finalize();
      onViewReady?.(null);
    };
  }, [spec, onViewReady]);

  return <div ref={containerRef} className="vega-chart-container" />;
}
