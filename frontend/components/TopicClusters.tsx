"use client";

import { useState, useEffect } from "react";

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

  if (loading) return <div className="card">Analyzing topic clusters...</div>;
  if (clusters.length === 0) return <div className="card text-gray-500">No topic clusters available. Data is still being collected.</div>;

  const topicEmojis: Record<string, string> = {
    "AI & Technology": "\uD83E\uDD16",
    "Health & Medicine": "\uD83C\uDFE5",
    "Climate & Environment": "\uD83C\uDF0D",
    "Politics & Government": "\uD83C\uDFDB\uFE0F",
    "Economy & Business": "\uD83D\uDCC8",
    "Science & Research": "\uD83D\uDD2C",
    "Social Media & Misinformation": "\u26A0\uFE0F",
    "Conflict & Security": "\uD83D\uDEA8",
    "Other": "\uD83D\uDCC1",
  };

  const getDominantSentiment = (s: ClusterSentiment) => {
    const total = s.positive + s.neutral + s.negative;
    if (total === 0) return { label: "neutral", color: "text-gray-500" };
    if (s.positive > s.neutral && s.positive > s.negative) return { label: "positive", color: "text-green-600" };
    if (s.negative > s.positive && s.negative > s.neutral) return { label: "negative", color: "text-red-600" };
    return { label: "neutral", color: "text-gray-600" };
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Topic Clusters</h2>
      <p className="text-gray-500 text-sm mb-4">
        Related topics grouped by keyword co-occurrence and engagement patterns.
      </p>
      <div className="space-y-3">
        {clusters.map((cluster) => {
          const dominant = getDominantSentiment(cluster.sentiment_distribution);
          const isExpanded = expandedCluster === cluster.topic;

          return (
            <div key={cluster.topic} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedCluster(isExpanded ? null : cluster.topic)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{topicEmojis[cluster.topic] || "\uD83D\uDCC1"}</span>
                  <div>
                    <div className="font-semibold">{cluster.topic}</div>
                    <div className="text-xs text-gray-500">
                      {cluster.post_count} posts &middot; {cluster.platforms.join(", ")} &middot; avg engagement: {cluster.avg_engagement.toFixed(0)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-medium ${dominant.color}`}>
                    {dominant.label}
                  </span>
                  <span className="text-gray-400">{isExpanded ? "\u25B2" : "\u25BC"}</span>
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 py-3 bg-gray-50 border-t">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <div className="text-xs text-gray-500">Posts</div>
                      <div className="font-bold">{cluster.post_count}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Avg Engagement</div>
                      <div className="font-bold">{cluster.avg_engagement.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Authority Score</div>
                      <div className="font-bold">{cluster.avg_authority_score.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Sentiment</div>
                      <div className="flex gap-2 text-xs">
                        <span className="text-green-600">{cluster.sentiment_distribution.positive} pos</span>
                        <span className="text-gray-500">{cluster.sentiment_distribution.neutral} neu</span>
                        <span className="text-red-600">{cluster.sentiment_distribution.negative} neg</span>
                      </div>
                    </div>
                  </div>

                  {cluster.top_keywords.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs text-gray-500 mb-1">Keywords</div>
                      <div className="flex flex-wrap gap-1">
                        {cluster.top_keywords.map((kw, i) => (
                          <span key={i} className="badge bg-blue-50 text-blue-700">#{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {cluster.related_topics.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Related Topics</div>
                      <div className="flex flex-wrap gap-2">
                        {cluster.related_topics.map((rt, i) => (
                          <span key={i} className="badge bg-gray-100 text-gray-700">
                            {rt.topic} ({(rt.similarity * 100).toFixed(0)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}