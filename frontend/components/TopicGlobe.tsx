"use client";

import { useEffect, useRef, useState } from "react";
import Globe from "react-globe.gl";

interface GlobePoint {
  lat: number;
  lng: number;
  size: number;
  sentiment: { positive: number; neutral: number; negative: number };
  name?: string;
}

interface GlobeArc {
  startLat: number;
  startLng: number;
  endLat: number;
  endLng: number;
}

interface GlobeData {
  topic?: string;
  points: GlobePoint[];
  arcs: GlobeArc[];
  total_posts?: number;
}

const MAP_URLS = {
  earthDark:
    "https://unpkg.com/three-globe/example/img/earth-night.jpg",
  earthDay:
    "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg",
  topology:
    "https://unpkg.com/three-globe/example/img/earth-topology.png",
};

export default function TopicGlobe({
  data,
  title,
}: {
  data: GlobeData | null;
  title?: string;
}) {
  const globeRef = useRef<any>();
  const [hoveredPoint, setHoveredPoint] = useState<GlobePoint | null>(null);
  const [dimensions, setDimensions] = useState({ width: 500, height: 400 });

  useEffect(() => {
    const updateDimensions = () => {
      const w = window.innerWidth;
      if (w < 768) setDimensions({ width: 340, height: 300 });
      else if (w < 1024) setDimensions({ width: 500, height: 400 });
      else setDimensions({ width: 600, height: 450 });
    };
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  if (!data || !data.points || data.points.length === 0) {
    return (
      <div className="border border-ink p-6 text-center">
        <p className="font-mono text-xs uppercase tracking-widest text-neutral-500">
          No geographic data available for this topic
        </p>
      </div>
    );
  }

  const pointsData = data.points.map((p) => {
    const total = p.sentiment.positive + p.sentiment.neutral + p.sentiment.negative;
    const posRatio = total > 0 ? p.sentiment.positive / total : 0;
    const negRatio = total > 0 ? p.sentiment.negative / total : 0;
    let color = "#737373";
    if (negRatio > 0.6) color = "#CC0000";
    else if (posRatio > 0.6) color = "#F9F9F7";

    return {
      lat: p.lat,
      lng: p.lng,
      size: Math.max(0.3, Math.min(2, p.size * 0.15)),
      color,
      label: `${p.name || "Unknown"} — ${p.sentiment.positive} pos / ${p.sentiment.neutral} neu / ${p.sentiment.negative} neg`,
      ...p,
    };
  });

  const arcsData = (data.arcs || []).map((a) => ({
    startLat: a.startLat,
    startLng: a.startLng,
    endLat: a.endLat,
    endLng: a.endLng,
  }));

  return (
    <div className="border border-ink bg-ink">
      {title && (
        <div className="border-b border-neutral-700 p-4">
          <h3 className="font-serif text-lg font-bold text-newsprint">
            {title}
          </h3>
          <p className="font-mono text-[10px] uppercase tracking-widest text-neutral-400 mt-1">
            Geographic sentiment distribution
            {data.total_posts ? ` · ${data.total_posts} posts` : ""}
          </p>
        </div>
      )}
      <div className="relative">
        <Globe
          ref={globeRef}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#111111"
          globeImageUrl={MAP_URLS.earthDark}
          bumpImageUrl={MAP_URLS.topology}
          pointsData={pointsData}
          pointLat="lat"
          pointLng="lng"
          pointAltitude={0.01}
          pointRadius="size"
          pointColor="color"
          onPointHover={(point: any) => {
            if (point) setHoveredPoint(point as unknown as GlobePoint);
            else setHoveredPoint(null);
          }}
          arcsData={arcsData}
          arcStartLat="startLat"
          arcStartLng="startLng"
          arcEndLat="endLat"
          arcEndLng="endLng"
          arcColor={() => "#CC0000"}
          arcDashLength={0.4}
          arcDashGap={0.2}
          arcDashAnimateTime={2000}
          arcStroke={0.8}
          atmosphereColor="#F9F9F7"
          atmosphereAltitude={0.12}
          enablePointerInteraction
        />
        {hoveredPoint && (
          <div className="absolute top-2 left-2 bg-newsprint border border-ink p-2 shadow-hard max-w-[200px]">
            <p className="font-sans text-xs font-bold">{hoveredPoint.name || "Unknown"}</p>
            <div className="flex gap-3 mt-1 font-mono text-[10px]">
              <span className="text-newsprint">{hoveredPoint.sentiment.positive} pos</span>
              <span className="text-neutral-600">{hoveredPoint.sentiment.neutral} neu</span>
              <span className="text-editorial-red">{hoveredPoint.sentiment.negative} neg</span>
            </div>
          </div>
        )}
      </div>
      <div className="flex justify-center gap-6 p-3 border-t border-neutral-700">
        <span className="flex items-center gap-2 font-mono text-xs text-newsprint">
          <span className="w-3 h-3 bg-newsprint rounded-full inline-block" />
          Positive
        </span>
        <span className="flex items-center gap-2 font-mono text-xs text-neutral-400">
          <span className="w-3 h-3 bg-neutral-500 rounded-full inline-block" />
          Neutral
        </span>
        <span className="flex items-center gap-2 font-mono text-xs text-editorial-red">
          <span className="w-3 h-3 bg-editorial-red rounded-full inline-block" />
          Negative
        </span>
      </div>
    </div>
  );
}