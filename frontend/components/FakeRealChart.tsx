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

  if (loading) return <div className="card">Loading sentiment data...</div>;

  const data = {
    labels: sentiment.map((s) => s.label || "Unknown"),
    datasets: [
      {
        data: sentiment.map((s) => s.count),
        backgroundColor: ["#22c55e", "#6b7280", "#ef4444"],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Sentiment Distribution</h2>
      {sentiment.length === 0 ? (
        <p className="text-gray-500">No sentiment data available</p>
      ) : (
        <div className="w-64 mx-auto">
          <Doughnut data={data} />
        </div>
      )}
    </div>
  );
}
