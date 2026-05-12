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

  if (loading) return <div className="card">Loading sentiment timeline...</div>;

  const chartData = {
    labels: sentiment.map((s) => s.label || "Unknown"),
    datasets: [
      {
        label: "Post Count",
        data: sentiment.map((s) => s.count),
        backgroundColor: ["#22c55e", "#6b7280", "#ef4444"],
      },
    ],
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Sentiment Overview</h2>
      {sentiment.length === 0 ? (
        <p className="text-gray-500">No data available</p>
      ) : (
        <Bar
          data={chartData}
          options={{
            responsive: true,
            plugins: {
              legend: { display: false },
            },
          }}
        />
      )}
    </div>
  );
}
