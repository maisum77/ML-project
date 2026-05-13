"use client";

import { useState, useEffect } from "react";
import { GitBranch, Loader2 } from "lucide-react";

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

const COLORS = ["#111111", "#CC0000", "#737373", "#404040", "#525252", "#A3A3A3"];

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
      <div className="border border-ink p-6">
        <div className="label-uppercase mb-4">Select 2-4 topics to compare across key metrics</div>

        <div className="flex flex-wrap gap-2 mb-6">
          {AVAILABLE_TOPICS.map((topic) => (
            <button
              key={topic}
              onClick={() => toggleTopic(topic)}
              className={`px-3 py-2 font-sans text-xs uppercase tracking-widest font-semibold transition-all duration-200 ${
                selected.includes(topic)
                  ? "bg-ink text-newsprint"
                  : "border border-ink hover:bg-ink hover:text-newsprint"
              }`}
            >
              {topic}
            </button>
          ))}
        </div>

        <button
          onClick={compare}
          disabled={selected.length < 2 || loading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Comparing..." : `Compare (${selected.length})`}
        </button>

        {error && <p className="mt-3 font-mono text-xs text-editorial-red uppercase tracking-widest">{error}</p>}
      </div>

      {data && data.comparison.length >= 2 && (
        <>
          <div className="border border-ink overflow-hidden">
            <div className="p-6 border-b-4 border-ink">
              <div className="label-uppercase mb-1">Section II</div>
              <h3 className="font-serif text-2xl font-black">Metrics Overview</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-4 border-ink">
                    <th className="text-left py-3 px-6 label-uppercase">Topic</th>
                    <th className="text-right py-3 px-6 label-uppercase">Posts</th>
                    <th className="text-right py-3 px-6 label-uppercase">Avg Engagement</th>
                    <th className="text-right py-3 px-6 label-uppercase">Authority Score</th>
                    <th className="text-left py-3 px-6 label-uppercase">Sentiment</th>
                  </tr>
                </thead>
                <tbody>
                  {data.comparison.map((item, i) => (
                    <tr key={item.topic} className="border-b border-ink hover:bg-neutral-100 transition-colors duration-200">
                      <td className="py-3 px-6 font-serif font-bold" style={{ color: COLORS[i % COLORS.length] }}>
                        {item.topic}
                      </td>
                      <td className="text-right py-3 px-6 font-mono">{item.post_count}</td>
                      <td className="text-right py-3 px-6 font-mono">{item.avg_engagement}</td>
                      <td className="text-right py-3 px-6 font-mono">{item.avg_authority_score}</td>
                      <td className="py-3 px-6">
                        <div className="flex gap-1 font-mono text-xs">
                          <span className="text-ink">{item.sentiment.positive_pct}%</span>
                          <span className="text-neutral-400">/</span>
                          <span className="text-neutral-500">{item.sentiment.neutral_pct}%</span>
                          <span className="text-neutral-400">/</span>
                          <span className="text-editorial-red">{item.sentiment.negative_pct}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-0 border border-ink">
            {(["post_count", "avg_engagement", "avg_authority_score"] as const).map((metric, mi) => {
              const labels: Record<string, string> = {
                post_count: "Posts",
                avg_engagement: "Avg Engagement",
                avg_authority_score: "Authority Score",
              };
              const max = data.metrics_max[metric] || 1;
              return (
                <div key={metric} className={`col-span-12 md:col-span-4 p-6 ${
                  mi < 2 ? "border-b md:border-b-0 md:border-r border-ink" : ""
                }`}>
                  <div className="label-uppercase mb-4">{labels[metric]}</div>
                  <div className="space-y-3">
                    {data.comparison.map((item, i) => (
                      <div key={item.topic}>
                        <div className="flex justify-between font-mono text-xs mb-1">
                          <span style={{ color: COLORS[i % COLORS.length] }}>{item.topic}</span>
                          <span className="font-bold">{item[metric]}</span>
                        </div>
                        <div className="w-full bg-newsprint-muted h-3">
                          <div
                            className="h-3 transition-all"
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

          <div className="border border-ink p-6">
            <div className="label-uppercase mb-4">Sentiment Breakdown</div>
            <div className="space-y-4">
              {data.comparison.map((item, i) => (
                <div key={item.topic}>
                  <div className="font-serif font-bold text-sm mb-1" style={{ color: COLORS[i % COLORS.length] }}>
                    {item.topic}
                  </div>
                  <div className="flex h-4 overflow-hidden">
                    <div className="bg-ink" style={{ width: `${item.sentiment.positive_pct}%` }} />
                    <div className="bg-newsprint-muted" style={{ width: `${item.sentiment.neutral_pct}%` }} />
                    <div className="bg-editorial-red" style={{ width: `${item.sentiment.negative_pct}%` }} />
                  </div>
                  <div className="flex justify-between font-mono text-xs mt-1">
                    <span className="text-ink">+{item.sentiment.positive_pct}%</span>
                    <span className="text-neutral-400">{item.sentiment.neutral_pct}%</span>
                    <span className="text-editorial-red">-{item.sentiment.negative_pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="border border-ink p-6">
            <div className="label-uppercase mb-4">Top Keywords</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.comparison.map((item, i) => (
                <div key={item.topic}>
                  <div className="font-serif font-bold text-sm mb-2" style={{ color: COLORS[i % COLORS.length] }}>
                    {item.topic}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {item.top_keywords.map((kw, ki) => (
                      <span
                        key={ki}
                        className="border border-ink px-2 py-0.5 font-mono text-xs"
                        style={{ borderColor: COLORS[i % COLORS.length] }}
                      >
                        #{kw}
                      </span>
                    ))}
                    {item.platforms.map((p) => (
                      <span key={p} className="bg-newsprint-muted px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest">
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