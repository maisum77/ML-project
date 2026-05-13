"use client";

import { useState, useEffect } from "react";
import { getOverallSentiment } from "../lib/api";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function SentimentTimeline() {
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

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading sentiment timeline...</div>;

  const chartData = {
    labels: sentiment.map((s) => s.label || "Unknown"),
    datasets: [
      {
        label: "Post Count",
        data: sentiment.map((s) => s.count),
        backgroundColor: ["#111111", "#E5E5E0", "#CC0000"],
        borderWidth: 1,
        borderColor: "#111111",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#111111",
        titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
        bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
      },
    },
    scales: {
      x: {
        ticks: { font: { family: "'Inter', sans-serif", size: 10 }, color: "#737373" },
        grid: { display: false },
        border: { color: "#111111", width: 2 },
      },
      y: {
        ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 }, color: "#737373" },
        grid: { color: "#E5E5E0" },
        border: { color: "#111111", width: 2 },
      },
    },
  };

  return (
    <div>
      {sentiment.length === 0 ? (
        <p className="font-body text-neutral-500 text-sm">No data available</p>
      ) : (
        <Bar data={chartData} options={options} />
      )}
    </div>
  );
}