"use client";

import { useState, useEffect } from "react";

interface TopicComparisonItem {
  topic: string;
  post_count: number;
  avg_engagement: number;
  avg_authority_score: number;
  sentiment: {
    positive_pct: number;
    neutral_pct: number;
    negative_pct: number;
  };
  platforms: string[];
  top_keywords: string[];
  relative_scores: Record<string, number>;
}

interface ComparisonData {
  comparison: TopicComparisonItem[];
  metrics_max: Record<string, number>;
  total_sentiment: Record<string, number>;
}

const AVAILABLE_TOPICS = [
  "AI & Technology",
  "Health & Medicine",
  "Climate & Environment",
  "Politics & Government",
  "Economy & Business",
  "Science & Research",
  "Social Media & Misinformation",
  "Conflict & Security",
];

const COLORS = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"];

export default function TopicComparison() {
  const [selected, setSelected] = useState<string[]>([]);
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggleTopic = (topic: string) => {
    setSelected((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : prev.length < 4 ? [...prev, topic] : prev
    );
  };

  const compare = async () => {
    if (selected.length < 2) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/trending/compare?topics=${encodeURIComponent(selected.join(","))}`
      );
      if (!res.ok) throw new Error("Failed to compare topics");
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Topic Comparison</h2>
        <p className="text-sm text-gray-500 mb-3">
          Select 2-4 topics to compare side by side across key metrics.
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {AVAILABLE_TOPICS.map((topic) => (
            <button
              key={topic}
              onClick={() => toggleTopic(topic)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                selected.includes(topic)
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {topic}
            </button>
          ))}
        </div>

        <button
          onClick={compare}
          disabled={selected.length < 2 || loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Comparing..." : `Compare (${selected.length})`}
        </button>

        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </div>

      {data && data.comparison.length >= 2 && (
        <>
          <div className="card">
            <h3 className="font-semibold mb-4">Metrics Overview</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Topic</th>
                    <th className="text-right py-2 px-3">Posts</th>
                    <th className="text-right py-2 px-3">Avg Engagement</th>
                    <th className="text-right py-2 px-3">Authority Score</th>
                    <th className="text-left py-2 px-3">Sentiment</th>
                  </tr>
                </thead>
                <tbody>
                  {data.comparison.map((item, i) => (
                    <tr key={item.topic} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-3 font-medium" style={{ color: COLORS[i % COLORS.length] }}>
                        {item.topic}
                      </td>
                      <td className="text-right py-2 px-3">{item.post_count}</td>
                      <td className="text-right py-2 px-3">{item.avg_engagement}</td>
                      <td className="text-right py-2 px-3">{item.avg_authority_score}</td>
                      <td className="py-2 px-3">
                        <div className="flex gap-1 text-xs">
                          <span className="text-green-600">{item.sentiment.positive_pct}%</span>
                          <span className="text-gray-400">/</span>
                          <span className="text-gray-600">{item.sentiment.neutral_pct}%</span>
                          <span className="text-gray-400">/</span>
                          <span className="text-red-600">{item.sentiment.negative_pct}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(["post_count", "avg_engagement", "avg_authority_score"] as const).map((metric, mi) => {
              const labels: Record<string, string> = {
                post_count: "Posts",
                avg_engagement: "Avg Engagement",
                avg_authority_score: "Authority Score",
              };
              const max = data.metrics_max[metric] || 1;
              return (
                <div key={metric} className="card">
                  <h4 className="text-sm font-semibold mb-3">{labels[metric]}</h4>
                  <div className="space-y-2">
                    {data.comparison.map((item, i) => (
                      <div key={item.topic}>
                        <div className="flex justify-between text-xs mb-1">
                          <span style={{ color: COLORS[i % COLORS.length] }}>{item.topic}</span>
                          <span className="font-mono">{item[metric]}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="h-3 rounded-full transition-all"
                            style={{
                              width: `${Math.max(5, (item[metric] / max) * 100)}%`,
                              backgroundColor: COLORS[i % COLORS.length],
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3">Sentiment Breakdown</h3>
            <div className="space-y-4">
              {data.comparison.map((item, i) => (
                <div key={item.topic}>
                  <div className="text-sm font-medium mb-1" style={{ color: COLORS[i % COLORS.length] }}>
                    {item.topic}
                  </div>
                  <div className="flex h-4 rounded-full overflow-hidden">
                    <div className="bg-green-500" style={{ width: `${item.sentiment.positive_pct}%` }} />
                    <div className="bg-gray-400" style={{ width: `${item.sentiment.neutral_pct}%` }} />
                    <div className="bg-red-500" style={{ width: `${item.sentiment.negative_pct}%` }} />
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className="text-green-600">+{item.sentiment.positive_pct}%</span>
                    <span className="text-gray-500">{item.sentiment.neutral_pct}%</span>
                    <span className="text-red-600">-{item.sentiment.negative_pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3">Top Keywords</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.comparison.map((item, i) => (
                <div key={item.topic}>
                  <div className="text-sm font-medium mb-2" style={{ color: COLORS[i % COLORS.length] }}>
                    {item.topic}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {item.top_keywords.map((kw, ki) => (
                      <span
                        key={ki}
                        className="px-2 py-0.5 rounded-full text-xs"
                        style={{ backgroundColor: `${COLORS[i % COLORS.length]}20`, color: COLORS[i % COLORS.length] }}
                      >
                        #{kw}
                      </span>
                    ))}
                    {item.platforms.map((p) => (
                      <span key={p} className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}