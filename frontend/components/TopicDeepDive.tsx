"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import { ArrowLeft, TrendingUp, BarChart3, RefreshCw, Wifi, WifiOff, Search } from "lucide-react";
import { getTopicClusters, getFeed, getSentiment, getPropagation, getTopicGeoGlobe } from "../lib/api";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";

const TopicGlobe = dynamic(() => import("./TopicGlobe"), { ssr: false });
const KnowledgeGraph = dynamic(() => import("./KnowledgeGraph"), { ssr: false });

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface Cluster {
  topic: string;
  post_count: number;
  avg_engagement: number;
  avg_authority_score: number;
  sentiment_distribution: { positive: number; neutral: number; negative: number };
  platforms: string[];
  top_keywords: string[];
  related_topics: Array<{ topic: string; similarity: number }>;
}

const POLL_INTERVAL = 30000;

export default function TopicDeepDive() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [customTopic, setCustomTopic] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [connectionOk, setConnectionOk] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const prevClusterTopics = useRef<Set<string>>(new Set());

  const [sentimentData, setSentimentData] = useState<any>(null);
  const [propagationData, setPropagationData] = useState<any>(null);
  const [globeData, setGlobeData] = useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const fetchClusters = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    try {
      const data = await getTopicClusters();
      setClusters(data.clusters || []);
      setLastUpdated(new Date());
      setConnectionOk(true);
      prevClusterTopics.current = new Set((data.clusters || []).map((c: Cluster) => c.topic));
    } catch (err) {
      console.error("Failed to fetch clusters:", err);
      setConnectionOk(false);
    } finally {
      setLoading(false);
      if (isManualRefresh) setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchClusters();
    const interval = setInterval(() => fetchClusters(), POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchClusters]);

  useEffect(() => {
    if (!selectedTopic) return;
    setLoadingAnalysis(true);
    Promise.all([
      getSentiment(selectedTopic).catch((e) => { console.error("Sentiment fetch failed:", e); return null; }),
      getPropagation(selectedTopic).catch((e) => { console.error("Propagation fetch failed:", e); return null; }),
      getTopicGeoGlobe(selectedTopic).catch((e) => { console.error("Globe fetch failed:", e); return null; }),
    ]).then(([sentiment, propagation, globe]) => {
      setSentimentData(sentiment);
      setPropagationData(propagation);
      setGlobeData(globe);
      setLoadingAnalysis(false);
    });
  }, [selectedTopic]);

  const handleCustomSearch = () => {
    const term = customTopic.trim();
    if (term) setSelectedTopic(term);
  };

  const timeSinceUpdate = lastUpdated
    ? Math.max(0, Math.floor((Date.now() - lastUpdated.getTime()) / 1000))
    : null;

  const formatTimeSince = (seconds: number) => {
    if (seconds < 5) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    return `${Math.floor(seconds / 60)}m ago`;
  };

  if (loading) {
    return (
      <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">
        Loading topic clusters from database...
      </div>
    );
  }

  const renderAnalysis = () => {
    const totalPosts = sentimentData?.timeline?.reduce((sum: number, t: any) => sum + t.count, 0) || 0;
    const positiveCount = sentimentData?.timeline?.filter((t: any) => t.sentiment === "positive").reduce((sum: number, t: any) => sum + t.count, 0) || 0;
    const negativeCount = sentimentData?.timeline?.filter((t: any) => t.sentiment === "negative").reduce((sum: number, t: any) => sum + t.count, 0) || 0;
    const neutralCount = sentimentData?.timeline?.filter((t: any) => t.sentiment === "neutral").reduce((sum: number, t: any) => sum + t.count, 0) || 0;
    const totalCount = positiveCount + negativeCount + neutralCount;

    const selectedCluster = clusters.find((c) => c.topic === selectedTopic);
    const pos = selectedCluster?.sentiment_distribution?.positive || positiveCount;
    const neu = selectedCluster?.sentiment_distribution?.neutral || neutralCount;
    const neg = selectedCluster?.sentiment_distribution?.negative || negativeCount;
    const clusterTotal = pos + neu + neg || 1;

    const doughnutData = clusterTotal > 0 ? {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [pos, neu, neg],
        backgroundColor: ["#111111", "#E5E5E0", "#CC0000"],
        borderWidth: 2,
        borderColor: "#111111",
      }],
    } : null;

    const barData = sentimentData?.timeline?.length > 0 ? {
      labels: Array.from(new Set(sentimentData.timeline.map((t: any) => t.hour.split("T")[1]?.split(":")[0] || t.hour))),
      datasets: [
        { label: "Positive", data: sentimentData.timeline.filter((t: any) => t.sentiment === "positive").map((t: any) => t.count), backgroundColor: "#111111" },
        { label: "Neutral", data: sentimentData.timeline.filter((t: any) => t.sentiment === "neutral").map((t: any) => t.count), backgroundColor: "#E5E5E0" },
        { label: "Negative", data: sentimentData.timeline.filter((t: any) => t.sentiment === "negative").map((t: any) => t.count), backgroundColor: "#CC0000" },
      ],
    } : null;

    const barOptions = {
      responsive: true,
      plugins: {
        legend: { position: "bottom" as const, labels: { font: { family: "'Inter', sans-serif", size: 10 }, padding: 12, usePointStyle: true, pointStyleWidth: 8, color: "#111111" } },
        tooltip: { backgroundColor: "#111111", titleFont: { family: "'JetBrains Mono', monospace", size: 11 }, bodyFont: { family: "'JetBrains Mono', monospace", size: 11 } },
      },
      scales: {
        x: { ticks: { font: { family: "'Inter', sans-serif", size: 9 }, color: "#737373" }, grid: { display: false }, border: { color: "#111111", width: 2 } },
        y: { ticks: { font: { family: "'JetBrains Mono', monospace", size: 9 }, color: "#737373" }, grid: { color: "#E5E5E0" }, border: { color: "#111111", width: 2 } },
      },
    };

    return (
      <div>
        <button
          onClick={() => setSelectedTopic(null)}
          className="flex items-center gap-2 mb-6 font-sans text-xs uppercase tracking-widest border border-ink px-3 py-2 hover:bg-ink hover:text-newsprint transition-all duration-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Topics
        </button>

        <div className="border-b-4 border-ink pb-2 mb-8">
          <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
            Deep Dive
          </h2>
          <p className="label-uppercase mt-2">
            Analysis of <span className="text-editorial-red font-bold">{selectedTopic}</span>
          </p>
          {selectedCluster && (
            <div className="flex flex-wrap gap-2 mt-3">
              {selectedCluster.platforms.map((p) => (
                <span key={p} className="border border-ink px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest">
                  {p}
                </span>
              ))}
              {selectedCluster.top_keywords.slice(0, 5).map((kw) => (
                <span key={kw} className="bg-newsprint-muted px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest">
                  #{kw}
                </span>
              ))}
            </div>
          )}
        </div>

        {loadingAnalysis ? (
          <div className="border border-ink p-12 text-center font-mono text-xs uppercase tracking-widest text-neutral-500">
            <BarChart3 className="h-6 w-6 mx-auto mb-3" strokeWidth={1.5} />
            Loading analysis data...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-ink p-6 bg-newsprint">
                <div className="label-uppercase text-neutral-500 mb-1">Total Posts</div>
                <div className="font-mono text-4xl font-black">{selectedCluster?.post_count || totalCount || "—"}</div>
              </div>
              <div className="border border-ink p-6 bg-newsprint">
                <div className="label-uppercase text-neutral-500 mb-1">Positive Sentiment</div>
                <div className="font-mono text-4xl font-black text-newsprint bg-ink px-2">
                  {clusterTotal > 0 ? `${Math.round((pos / clusterTotal) * 100)}%` : "—"}
                </div>
              </div>
              <div className="border border-ink p-6 bg-newsprint">
                <div className="label-uppercase text-neutral-500 mb-1">Negative Sentiment</div>
                <div className="font-mono text-4xl font-black text-newsprint bg-editorial-red px-2">
                  {clusterTotal > 0 ? `${Math.round((neg / clusterTotal) * 100)}%` : "—"}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="border border-ink p-6 bg-newsprint">
                <h3 className="font-serif text-xl font-bold mb-4 border-b-2 border-ink pb-2">
                  Sentiment Breakdown
                </h3>
                {doughnutData ? (
                  <div className="max-w-[240px] mx-auto">
                    <Doughnut
                      data={doughnutData}
                      options={{
                        responsive: true,
                        plugins: {
                          legend: { position: "bottom" as const, labels: { font: { family: "'Inter', sans-serif", size: 11 }, padding: 16, usePointStyle: true, pointStyleWidth: 8, color: "#111111" } },
                          tooltip: { backgroundColor: "#111111", titleFont: { family: "'JetBrains Mono', monospace", size: 11 }, bodyFont: { family: "'JetBrains Mono', monospace", size: 11 } },
                        },
                        cutout: "60%",
                      }}
                    />
                  </div>
                ) : (
                  <p className="font-body text-neutral-500 text-sm">No sentiment data available</p>
                )}
                <div className="mt-4 pt-4 border-t border-newsprint-muted">
                  <div className="flex justify-between items-center py-1 border-b border-newsprint-muted">
                    <span className="font-sans text-xs uppercase tracking-widest">Positive</span>
                    <span className="font-mono text-sm font-semibold">{pos}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-newsprint-muted">
                    <span className="font-sans text-xs uppercase tracking-widest">Neutral</span>
                    <span className="font-mono text-sm font-semibold">{neu}</span>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="font-sans text-xs uppercase tracking-widest">Negative</span>
                    <span className="font-mono text-sm font-semibold">{neg}</span>
                  </div>
                </div>
              </div>

              <div className="border border-ink p-6 bg-newsprint">
                <h3 className="font-serif text-xl font-bold mb-4 border-b-2 border-ink pb-2">
                  Sentiment Timeline
                </h3>
                {barData ? (
                  <Bar data={barData} options={barOptions} />
                ) : (
                  <p className="font-body text-neutral-500 text-sm">No timeline data available</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TopicGlobe data={globeData} title={`${selectedTopic} — Global Sentiment`} />
              <KnowledgeGraph data={propagationData} />
            </div>
          </div>
        )}
      </div>
    );
  };

  if (selectedTopic) return renderAnalysis();

  return (
    <div>
      <div className="border-b-4 border-ink pb-2 mb-6">
        <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
          Deep Dive
        </h2>
        <p className="label-uppercase mt-2">
          Select a topic cluster for full analysis from stored data
        </p>
      </div>

      <div className="flex items-center justify-between mb-4 border border-ink p-3">
        <div className="flex items-center gap-3">
          {connectionOk ? (
            <span className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
              </span>
              <span className="font-mono text-[10px] uppercase tracking-widest text-green-600">
                Live
              </span>
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <WifiOff className="h-3 w-3 text-editorial-red" strokeWidth={2} />
              <span className="font-mono text-[10px] uppercase tracking-widest text-editorial-red">
                Connection lost — retrying...
              </span>
            </span>
          )}
          {lastUpdated && (
            <span className="font-mono text-[10px] uppercase tracking-widest text-neutral-400">
              Updated {formatTimeSince(timeSinceUpdate || 0)}
            </span>
          )}
        </div>
        <button
          onClick={() => fetchClusters(true)}
          disabled={refreshing}
          className="flex items-center gap-2 font-sans text-xs uppercase tracking-widest border border-ink px-3 py-1.5 hover:bg-ink hover:text-newsprint transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} strokeWidth={2} />
          Refresh
        </button>
      </div>

      <div className="flex gap-2 mb-6 border border-ink p-4">
        <input
          type="text"
          value={customTopic}
          onChange={(e) => setCustomTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCustomSearch()}
          placeholder="Search any topic (e.g., climate, AI, health)..."
          className="flex-1 newsprint-input"
          style={{ borderRadius: 0 }}
        />
        <button
          onClick={handleCustomSearch}
          disabled={!customTopic.trim()}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Search className="h-4 w-4" strokeWidth={2} />
          Analyze
        </button>
      </div>

      {clusters.length === 0 ? (
        <div className="border border-ink p-12 text-center font-mono text-xs uppercase tracking-widest text-neutral-500">
          <TrendingUp className="h-6 w-6 mx-auto mb-3" strokeWidth={1.5} />
          No topic clusters found in the database. Try refreshing.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clusters.map((cluster, index) => {
            const pos = cluster.sentiment_distribution?.positive || 0;
            const neu = cluster.sentiment_distribution?.neutral || 0;
            const neg = cluster.sentiment_distribution?.negative || 0;
            const total = pos + neu + neg || 1;
            const isNew = !prevClusterTopics.current.has(cluster.topic);

            return (
              <button
                key={cluster.topic}
                onClick={() => setSelectedTopic(cluster.topic)}
                className={`border border-ink p-5 bg-newsprint hover:shadow-hard hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all duration-200 text-left group ${isNew ? "ring-2 ring-editorial-red ring-offset-2 ring-offset-newsprint" : ""}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {index === 0 && (
                      <span className="bg-editorial-red text-newsprint px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold">
                        Hot
                      </span>
                    )}
                    <span className="font-sans text-xs uppercase tracking-widest text-neutral-500">
                      {cluster.post_count} post{cluster.post_count !== 1 ? "s" : ""}
                    </span>
                  </div>
                  <TrendingUp className="h-4 w-4 text-neutral-400 group-hover:text-editorial-red transition-colors" strokeWidth={1.5} />
                </div>

                <h3 className="font-serif text-xl font-bold leading-tight group-hover:text-editorial-red transition-colors duration-200">
                  {cluster.topic}
                </h3>

                <div className="mt-3 flex items-center gap-3 text-xs font-mono">
                  <span className="text-neutral-600">
                    {Math.round(cluster.avg_engagement)} avg engagement
                  </span>
                  <span className="text-neutral-400">
                    Authority: {cluster.avg_authority_score}
                  </span>
                </div>

                {cluster.top_keywords.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {cluster.top_keywords.slice(0, 4).map((kw) => (
                      <span key={kw} className="bg-newsprint-muted px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-widest text-neutral-600">
                        #{kw}
                      </span>
                    ))}
                  </div>
                )}

                <div className="mt-3 flex gap-1 h-2">
                  <div
                    className="bg-ink"
                    style={{ width: `${(pos / total) * 100}%`, minWidth: pos > 0 ? "4px" : "0" }}
                  />
                  <div
                    className="bg-newsprint-muted"
                    style={{ width: `${(neu / total) * 100}%`, minWidth: neu > 0 ? "4px" : "0" }}
                  />
                  <div
                    className="bg-editorial-red"
                    style={{ width: `${(neg / total) * 100}%`, minWidth: neg > 0 ? "4px" : "0" }}
                  />
                </div>
                <div className="mt-1 flex justify-between font-mono text-[10px] text-neutral-500 uppercase tracking-widest">
                  <span>{pos} pos</span>
                  <span>{neu} neu</span>
                  <span>{neg} neg</span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}