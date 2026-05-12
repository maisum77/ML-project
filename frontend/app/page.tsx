"use client";

import { useState, useEffect } from "react";
import TrendingTopics from "../components/TrendingTopics";
import FakeRealChart from "../components/FakeRealChart";
import SentimentTimeline from "../components/SentimentTimeline";
import PostExplorer from "../components/PostExplorer";
import LiveFeed from "../components/LiveFeed";
import GlobeView from "../components/GlobeView";
import PropagationGraph from "../components/PropagationGraph";
import TextClassifier from "../components/TextClassifier";
import SourceScorecard from "../components/SourceScorecard";
import TopicClusters from "../components/TopicClusters";
import TopicComparison from "../components/TopicComparison";
import ReportExport from "../components/ReportExport";
import NotificationBadge from "../components/NotificationBadge";
import { AuthProvider, useAuth } from "../lib/auth";
import AuthForm from "../components/AuthForm";
import UserDashboard from "../components/UserDashboard";
import { getGlobeData, getPropagation } from "../lib/api";

const TABS = [
  { id: "dashboard", label: "Dashboard", icon: "\uD83C\uDFE0" },
  { id: "classify", label: "Classify", icon: "\uD83D\uDD0D" },
  { id: "trends", label: "Clusters", icon: "\uD83D\uDCCA" },
  { id: "compare", label: "Compare", icon: "\u2696\uFE0F" },
  { id: "sources", label: "Sources", icon: "\u2705" },
  { id: "feed", label: "Feed", icon: "\uD83D\uDCDC" },
  { id: "explorer", label: "Explorer", icon: "\uD83D\uDD0E" },
  { id: "globe", label: "Globe", icon: "\uD83C\uDF0D" },
  { id: "propagation", label: "Propagation", icon: "\uD83D\uDD78\uFE0F" },
  { id: "export", label: "Export", icon: "\uD83D\uDCE4" },
  { id: "profile", label: "Profile", icon: "\uD83D\uDC64" },
];

function HomeContent() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [globeData, setGlobeData] = useState<any>(null);
  const [propagationData, setPropagationData] = useState<any>(null);
  const [propagationTopic, setPropagationTopic] = useState("mental health");
  const [loadingGlobe, setLoadingGlobe] = useState(false);
  const [loadingProp, setLoadingProp] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("socialpulse_dark");
    if (saved === "true") setDarkMode(true);
  }, []);

  const toggleDark = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem("socialpulse_dark", String(next));
  };

  useEffect(() => {
    if (activeTab === "globe") {
      setLoadingGlobe(true);
      getGlobeData()
        .then(setGlobeData)
        .catch((err) => console.error("Globe data fetch failed:", err.message))
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
      .catch((err) => console.error("Propagation fetch failed:", err.message))
      .finally(() => setLoadingProp(false));
  };

  return (
    <div className={`min-h-screen ${darkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>
      <header className={`${darkMode ? "bg-gray-800 border-gray-700" : "bg-white"} shadow-sm border-b sticky top-0 z-10`}>
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">SocialPulse AI</h1>
              <p className="text-xs text-gray-500">Real-Time Misinformation & Trend Analyzer</p>
            </div>
            <span className="text-xs text-gray-400">v2.0</span>
            <NotificationBadge />
            <button
              onClick={toggleDark}
              className="ml-2 p-1.5 rounded-lg text-sm hover:bg-gray-200"
              title={darkMode ? "Light mode" : "Dark mode"}
            >
              {darkMode ? "\u2600\uFE0F" : "\uD83C\uDF19"}
            </button>
          </div>
          <nav className="flex gap-1 overflow-x-auto pb-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span className="mr-1">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
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

        {activeTab === "classify" && <TextClassifier />}
        {activeTab === "trends" && <TopicClusters />}
        {activeTab === "compare" && <TopicComparison />}
        {activeTab === "sources" && <SourceScorecard />}
        {activeTab === "feed" && <LiveFeed fullView />}
        {activeTab === "explorer" && <PostExplorer />}

        {activeTab === "globe" && (
          <div className="max-w-7xl mx-auto">
            {loadingGlobe ? (
              <div className="text-center py-12 text-gray-400">Loading globe data...</div>
            ) : (
              <GlobeView data={globeData} />
            )}
          </div>
        )}

        {activeTab === "propagation" && (
          <div className="max-w-7xl mx-auto space-y-4">
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

        {activeTab === "export" && <ReportExport />}

        {activeTab === "profile" && (
          user ? <UserDashboard /> : <AuthForm />
        )}
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <HomeContent />
    </AuthProvider>
  );
}