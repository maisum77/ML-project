"use client";

import { useEffect, useRef } from "react";

interface GlobeData {
  points: Array<{
    lat: number;
    lng: number;
    size: number;
    sentiment: { positive: number; neutral: number; negative: number };
  }>;
  arcs: Array<{
    startLat: number;
    startLng: number;
    endLat: number;
    endLng: number;
  }>;
}

export default function GlobeView({ data }: { data: GlobeData | null }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width;
    const H = canvas.height;
    const cx = W / 2;
    const cy = H / 2;
    const R = Math.min(cx, cy) - 30;

    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(0, 0, W, H);

      // Globe
      ctx.beginPath();
      ctx.arc(cx, cy, R, 0, Math.PI * 2);
      ctx.fillStyle = "#1e293b";
      ctx.fill();
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Grid lines
      ctx.strokeStyle = "#1e3a5f";
      ctx.lineWidth = 0.5;
      for (let lat = -60; lat <= 60; lat += 30) {
        const y = cy - (lat / 90) * R;
        const rx = R * Math.cos((lat * Math.PI) / 180);
        ctx.beginPath();
        ctx.ellipse(cx, y, rx, 2, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      for (let lng = -180; lng < 180; lng += 30) {
        const angle = (lng * Math.PI) / 180;
        ctx.beginPath();
        ctx.moveTo(cx, cy - R);
        ctx.lineTo(cx + R * Math.sin(angle), cy);
        ctx.lineTo(cx, cy + R);
        ctx.stroke();
      }

      // Arcs
      for (const arc of data.arcs || []) {
        const x1 = cx + (arc.startLng / 180) * R * 0.8;
        const y1 = cy - (arc.startLat / 90) * R * 0.8;
        const x2 = cx + (arc.endLng / 180) * R * 0.8;
        const y2 = cy - (arc.endLat / 90) * R * 0.8;
        const midX = (x1 + x2) / 2;
        const midY = Math.min(y1, y2) - Math.abs(y2 - y1) * 0.3 - 20;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.quadraticCurveTo(midX, midY, x2, y2);
        ctx.strokeStyle = "rgba(59, 130, 246, 0.3)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Points
      const maxSize = Math.max(...data.points.map((p) => p.size), 1);
      for (const point of data.points || []) {
        const x = cx + (point.lng / 180) * R * 0.85;
        const y = cy - (point.lat / 90) * R * 0.85;
        const radius = Math.max(3, (point.size / maxSize) * 12);

        const posRatio = point.sentiment.positive / point.size || 0;
        const negRatio = point.sentiment.negative / point.size || 0;

        ctx.beginPath();
        ctx.arc(x, y, radius + 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(59, 130, 246, 0.15)`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);

        if (negRatio > 0.6) {
          ctx.fillStyle = `rgba(239, 68, 68, 0.8)`;
        } else if (posRatio > 0.6) {
          ctx.fillStyle = `rgba(34, 197, 94, 0.8)`;
        } else {
          ctx.fillStyle = `rgba(59, 130, 246, 0.8)`;
        }
        ctx.fill();
      }

      requestAnimationFrame(draw);
    };

    draw();
  }, [data]);

  if (!data) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 text-center">
        <p className="text-gray-400">Loading globe data...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <h2 className="text-lg font-semibold text-white mb-3">Global Distribution</h2>
      <canvas
        ref={canvasRef}
        width={560}
        height={400}
        className="w-full rounded"
        style={{ maxHeight: "400px" }}
      />
      <div className="flex justify-center gap-4 mt-3 text-xs text-gray-400">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
          Positive
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" />
          Neutral
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />
          Negative
        </span>
      </div>
    </div>
  );
}
