"use client";

import { useState, useEffect } from "react";
import { getTrendingRealtime } from "../lib/api";

export default function TrendingTopics() {
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const data = await getTrendingRealtime(1);
        setTopics(data.trending || []);
      } catch (err) {
        console.error("Failed to fetch trending:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrending();
    const interval = setInterval(fetchTrending, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="card">Loading trending topics...</div>;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Trending Topics</h2>
      {topics.length === 0 ? (
        <p className="text-gray-500">No trending data available</p>
      ) : (
        <ul className="space-y-3">
          {topics.map((topic, i) => (
            <li key={topic._id || i} className="border-b pb-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">{topic._id || "Unknown"}</span>
                <span className="text-sm text-gray-500">
                  {topic.count} posts | Avg engagement: {Math.round(topic.avg_engagement || 0)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
