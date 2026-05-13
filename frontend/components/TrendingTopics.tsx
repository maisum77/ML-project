"use client";

import { useState, useEffect } from "react";
import { getTrendingRealtime } from "../lib/api";
import { TrendingUp } from "lucide-react";

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

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading trending topics...</div>;

  return (
    <div>
      {topics.length === 0 ? (
        <p className="font-body text-neutral-500 text-sm">No trending data available</p>
      ) : (
        <ul className="space-y-0">
          {topics.map((topic, i) => (
            <li key={topic._id || i} className="border-b border-ink py-3 last:border-b-0 group">
              <div className="flex justify-between items-start">
                <div className="flex items-start gap-3">
                  <span className="font-mono text-xs text-neutral-400 mt-0.5 min-w-[2rem]">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <span className="font-serif font-bold text-lg group-hover:text-editorial-red transition-colors duration-200">
                      {topic._id || "Unknown"}
                    </span>
                    {i === 0 && (
                      <span className="ml-2 bg-editorial-red text-newsprint px-1.5 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold">
                        Hot
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right font-mono text-xs text-neutral-500">
                  <div>{topic.count} posts</div>
                  <div className="text-neutral-400">eng: {Math.round(topic.avg_engagement || 0)}</div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}