"use client";

import { useState, useEffect } from "react";
import TrendingTopics from "../components/TrendingTopics";
import FakeRealChart from "../components/FakeRealChart";
import SentimentTimeline from "../components/SentimentTimeline";
import PostExplorer from "../components/PostExplorer";
import LiveFeed from "../components/LiveFeed";
import GlobeView from "../components/GlobeView";
import PropagationGraph from "../components/PropagationGraph";
import { getGlobeData, getPropagation, getTrending } from "../lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [globeData, setGlobeData] = useState<any>(null);
  const [propagationData, setPropagationData] = useState<any>(null);
  const [propagationTopic, setPropagationTopic] = useState("mental health");
  const [loadingGlobe, setLoadingGlobe] = useState(false);
  const [loadingProp, setLoadingProp] = useState(false);

  useEffect(() => {
    if (activeTab === "globe") {
      setLoadingGlobe(true);
      getGlobeData()
        .then(setGlobeData)
        .catch(() => {})
        .finally(() => setLoadingGlobe(false));
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "propagation") {
      loadPropagation(propagationTopic);
    }
  }, [activeTab]);

  const loadPropagation = (topic: string) => {
    setLoadingProp(true);
    getPropagation(topic)
      .then(setPropagationData)
      .catch(() => {})
      .finally(() => setLoadingProp(false));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">SocialPulse AI</h1>
            <nav className="flex gap-2">
              {["dashboard", "feed", "explorer", "globe", "propagation"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded capitalize transition text-sm ${
                    activeTab === tab
                      ? "bg-blue-600 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === "dashboard" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TrendingTopics />
            <FakeRealChart />
            <SentimentTimeline />
            <LiveFeed />
          </div>
        )}

        {activeTab === "feed" && <LiveFeed fullView />}
        {activeTab === "explorer" && <PostExplorer />}

        {activeTab === "globe" && (
          <div className="max-w-2xl mx-auto">
            {loadingGlobe ? (
              <div className="text-center py-12 text-gray-400">Loading globe data...</div>
            ) : (
              <GlobeView data={globeData} />
            )}
          </div>
        )}

        {activeTab === "propagation" && (
          <div className="max-w-2xl mx-auto space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={propagationTopic}
                onChange={(e) => setPropagationTopic(e.target.value)}
                placeholder="Enter topic (e.g., mental health)"
                className="flex-1 px-3 py-2 border rounded text-sm"
              />
              <button
                onClick={() => loadPropagation(propagationTopic)}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Trace
              </button>
            </div>
            {loadingProp ? (
              <div className="text-center py-12 text-gray-400">Tracing propagation...</div>
            ) : (
              <PropagationGraph data={propagationData} />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
