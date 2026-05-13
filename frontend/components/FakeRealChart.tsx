"use client";

import { useState, useEffect } from "react";
import { getOverallSentiment } from "../lib/api";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function FakeRealChart() {
  const [sentiment, setSentiment] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSentiment = async () => {
      try {
        const data = await getOverallSentiment();
        setSentiment(data.sentiment_breakdown || []);
      } catch (err) {
        console.error("Failed to fetch sentiment:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchSentiment();
  }, []);

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading sentiment data...</div>;

  const data = {
    labels: sentiment.map((s) => s.label || "Unknown"),
    datasets: [
      {
        data: sentiment.map((s) => s.count),
        backgroundColor: ["#111111", "#E5E5E0", "#CC0000"],
        borderWidth: 2,
        borderColor: "#111111",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom" as const,
        labels: {
          font: { family: "'Inter', sans-serif", size: 11 },
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 8,
          color: "#111111",
        },
      },
      tooltip: {
        backgroundColor: "#111111",
        titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
        bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
      },
    },
    cutout: "60%",
  };

  return (
    <div>
      {sentiment.length === 0 ? (
        <p className="font-body text-neutral-500 text-sm">No sentiment data available</p>
      ) : (
        <div className="max-w-[240px] mx-auto">
          <Doughnut data={data} options={options} />
        </div>
      )}
      <div className="mt-4 pt-4 border-t border-newsprint-muted">
        {sentiment.map((s) => (
          <div key={s.label} className="flex justify-between items-center py-1 border-b border-newsprint-muted last:border-b-0">
            <span className="font-sans text-xs uppercase tracking-widest">{s.label || "Unknown"}</span>
            <span className="font-mono text-sm font-semibold">{s.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}