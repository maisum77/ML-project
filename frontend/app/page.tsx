"use client";

import { useState, useEffect } from "react";
import TrendingTopics from "../components/TrendingTopics";
import FakeRealChart from "../components/FakeRealChart";
import SentimentTimeline from "../components/SentimentTimeline";
import PostExplorer from "../components/PostExplorer";
import LiveFeed from "../components/LiveFeed";

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">SocialPulse AI</h1>
            <nav className="flex gap-4">
              {["dashboard", "feed", "explorer"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded capitalize transition ${
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
      </main>
    </div>
  );
}
