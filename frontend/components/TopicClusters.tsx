"use client";

import { useState, useEffect } from "react";
import { ChevronDown } from "lucide-react";

interface ClusterSentiment {
  positive: number;
  neutral: number;
  negative: number;
}

interface RelatedTopic {
  topic: string;
  similarity: number;
}

interface Cluster {
  topic: string;
  post_count: number;
  avg_engagement: number;
  avg_authority_score: number;
  sentiment_distribution: ClusterSentiment;
  platforms: string[];
  top_keywords: string[];
  related_topics: RelatedTopic[];
}

export default function TopicClusters() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedCluster, setExpandedCluster] = useState<string | null>(null);

  useEffect(() => {
    const fetchClusters = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/trending/clusters`
        );
        if (res.ok) {
          const data = await res.json();
          setClusters(data.clusters || []);
        }
      } catch (err) {
        console.error("Failed to fetch clusters:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchClusters();
  }, []);

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Analyzing topic clusters...</div>;
  if (clusters.length === 0) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500">No topic clusters available. Data is still being collected.</div>;

  const getDominantSentiment = (s: ClusterSentiment) => {
    const total = s.positive + s.neutral + s.negative;
    if (total === 0) return { label: "neutral", color: "text-neutral-500", border: "border-neutral-500" };
    if (s.positive > s.neutral && s.positive > s.negative) return { label: "positive", color: "text-ink", border: "border-ink" };
    if (s.negative > s.positive && s.negative > s.neutral) return { label: "negative", color: "text-editorial-red", border: "border-editorial-red" };
    return { label: "neutral", color: "text-neutral-500", border: "border-neutral-500" };
  };

  return (
    <div className="space-y-0">
      {clusters.map((cluster) => {
        const dominant = getDominantSentiment(cluster.sentiment_distribution);
        const isExpanded = expandedCluster === cluster.topic;

        return (
          <div key={cluster.topic} className="border-b border-ink last:border-b-0">
            <button
              onClick={() => setExpandedCluster(isExpanded ? null : cluster.topic)}
              className="w-full text-left px-6 py-4 hover:bg-neutral-100 transition-colors duration-200 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <span className={`font-serif text-lg font-bold ${dominant.color}`}>
                  {cluster.topic}
                </span>
                <span className={`border ${dominant.border} px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest`}>
                  {dominant.label}
                </span>
              </div>
              <div className="flex items-center gap-4">
                <span className="font-mono text-xs text-neutral-400">
                  {cluster.post_count} posts &middot; avg eng: {cluster.avg_engagement.toFixed(0)}
                </span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`} strokeWidth={1.5} />
              </div>
            </button>

            <div className={`grid transition-all duration-300 ease-in-out ${isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
              <div className="overflow-hidden">
                <div className="px-6 py-4 bg-neutral-100 border-t border-ink">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <div className="label-uppercase text-neutral-400">Posts</div>
                      <div className="font-serif text-2xl font-black">{cluster.post_count}</div>
                    </div>
                    <div>
                      <div className="label-uppercase text-neutral-400">Avg Engagement</div>
                      <div className="font-serif text-2xl font-black">{cluster.avg_engagement.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="label-uppercase text-neutral-400">Authority Score</div>
                      <div className="font-serif text-2xl font-black">{cluster.avg_authority_score.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="label-uppercase text-neutral-400">Sentiment</div>
                      <div className="flex gap-3 font-mono text-xs mt-2">
                        <span className="text-ink">{cluster.sentiment_distribution.positive} pos</span>
                        <span className="text-neutral-400">{cluster.sentiment_distribution.neutral} neu</span>
                        <span className="text-editorial-red">{cluster.sentiment_distribution.negative} neg</span>
                      </div>
                    </div>
                  </div>

                  {cluster.top_keywords.length > 0 && (
                    <div className="mb-4">
                      <div className="label-uppercase text-neutral-400 mb-2">Keywords</div>
                      <div className="flex flex-wrap gap-2">
                        {cluster.top_keywords.map((kw, i) => (
                          <span key={i} className="border border-ink px-2 py-0.5 font-mono text-xs">#{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {cluster.related_topics.length > 0 && (
                    <div>
                      <div className="label-uppercase text-neutral-400 mb-2">Related Topics</div>
                      <div className="flex flex-wrap gap-2">
                        {cluster.related_topics.map((rt, i) => (
                          <span key={i} className="bg-newsprint-muted px-2 py-0.5 font-sans text-xs uppercase tracking-widest">
                            {rt.topic} ({(rt.similarity * 100).toFixed(0)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}