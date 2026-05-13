"use client";

import { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import {
  Search,
  BarChart3,
  GitBranch,
  CheckCircle,
  FileText,
  Globe,
  Network,
  Download,
  User,
  Menu,
  X,
  AlertTriangle,
  TrendingUp,
  Bell,
  Crosshair,
} from "lucide-react";
import TrendingTopics from "../components/TrendingTopics";
import FakeRealChart from "../components/FakeRealChart";
import SentimentTimeline from "../components/SentimentTimeline";
import PostExplorer from "../components/PostExplorer";
import LiveFeed from "../components/LiveFeed";
import dynamic from "next/dynamic";
const GlobeView = dynamic(() => import("../components/GlobeView"), { ssr: false });
import PropagationGraph from "../components/PropagationGraph";
import TextClassifier from "../components/TextClassifier";
import SourceScorecard from "../components/SourceScorecard";
import TopicClusters from "../components/TopicClusters";
import TopicComparison from "../components/TopicComparison";
import TopicDeepDive from "../components/TopicDeepDive";
import ReportExport from "../components/ReportExport";
import NotificationBadge from "../components/NotificationBadge";
import { AuthProvider, useAuth } from "../lib/auth";
import AuthForm from "../components/AuthForm";
import UserDashboard from "../components/UserDashboard";
import { getGlobeData, getPropagation } from "../lib/api";

const TABS = [
  { id: "dashboard", label: "Dashboard", icon: TrendingUp },
  { id: "deepdive", label: "Deep Dive", icon: Crosshair },
  { id: "classify", label: "Classify", icon: Search },
  { id: "trends", label: "Clusters", icon: BarChart3 },
  { id: "compare", label: "Compare", icon: GitBranch },
  { id: "sources", label: "Sources", icon: CheckCircle },
  { id: "feed", label: "Feed", icon: FileText },
  { id: "explorer", label: "Explorer", icon: Search },
  { id: "globe", label: "Globe", icon: Globe },
  { id: "propagation", label: "Propagation", icon: Network },
  { id: "export", label: "Export", icon: Download },
  { id: "profile", label: "Profile", icon: User },
];

const TICKER_ITEMS = [
  "LIVE TRACKING — 12,847 posts analyzed in the last hour",
  "ALERT — Misinformation spike detected in health sector",
  "TRENDING — Climate policy discussions up 23%",
  "AUTHORITY — 847 verified sources now tracked",
  "REAL-TIME — Sentiment analysis running on 4 platforms",
];

function TickerBar() {
  return (
    <div className="bg-ink text-newsprint overflow-hidden">
      <div className="flex items-center">
        <div className="bg-editorial-red text-newsprint px-4 py-2 font-mono text-xs uppercase tracking-widest shrink-0 font-bold">
          LIVE
        </div>
        <div className="overflow-hidden flex-1">
          <div className="ticker-animation flex whitespace-nowrap">
            {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
              <span key={i} className="px-8 font-mono text-xs py-2 inline-block">
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function HomeContent() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [globeData, setGlobeData] = useState<any>(null);
  const [propagationData, setPropagationData] = useState<any>(null);
  const [propagationTopic, setPropagationTopic] = useState("mental health");
  const [loadingGlobe, setLoadingGlobe] = useState(false);
  const [loadingProp, setLoadingProp] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mainRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (headerRef.current) {
      gsap.fromTo(
        headerRef.current,
        { y: -100, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }
      );
    }
  }, []);

  useEffect(() => {
    if (mainRef.current) {
      gsap.fromTo(
        mainRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
      );
    }
  }, [activeTab]);

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

  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="min-h-screen bg-newsprint">
      <TickerBar />

      <header ref={headerRef} className="border-b-4 border-ink sticky top-0 z-40 bg-newsprint">
        <div className="max-w-screen-xl mx-auto px-4">
          <div className="flex items-center justify-between py-4 border-b border-ink">
            <div>
              <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-black tracking-tighter leading-[0.9] text-ink">
                SOCIAL<span className="text-editorial-red">PULSE</span>
              </h1>
              <p className="label-uppercase mt-1">
                Real-Time Misinformation & Trend Analyzer
              </p>
            </div>
            <div className="hidden lg:flex items-center gap-6">
              <span className="font-mono text-xs text-neutral-500">
                Vol. 1 &middot; {today} &middot; New York Edition
              </span>
              <NotificationBadge />
            </div>
            <button
              className="lg:hidden p-2 border border-ink min-h-[44px] min-w-[44px] flex items-center justify-center hover:bg-ink hover:text-newsprint transition-all duration-200"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" strokeWidth={1.5} /> : <Menu className="h-5 w-5" strokeWidth={1.5} />}
            </button>
          </div>

          <nav className="hidden lg:flex border-b border-ink">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 font-sans text-xs uppercase tracking-widest font-semibold transition-all duration-200 border-r border-ink last:border-r-0 min-h-[44px] flex items-center gap-2 ${
                    activeTab === tab.id
                      ? "bg-ink text-newsprint"
                      : "text-ink hover:bg-neutral-100"
                  }`}
                >
                  <Icon className="h-4 w-4" strokeWidth={1.5} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {mobileMenuOpen && (
        <div className="lg:hidden border-b-4 border-ink bg-newsprint z-40 relative">
          <nav className="max-w-screen-xl mx-auto">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full px-4 py-3 font-sans text-xs uppercase tracking-widest font-semibold transition-all duration-200 border-b border-newsprint-muted flex items-center gap-3 min-h-[44px] text-left ${
                    activeTab === tab.id
                      ? "bg-ink text-newsprint"
                      : "text-ink hover:bg-neutral-100"
                  }`}
                >
                  <Icon className="h-4 w-4" strokeWidth={1.5} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      )}

      <main ref={mainRef} className="max-w-screen-xl mx-auto px-4 py-8">
        {activeTab === "dashboard" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Front Page
              </h2>
              <p className="label-uppercase mt-2">
                Latest intelligence &middot; Updated in real-time
              </p>
            </div>

            <div className="grid grid-cols-12 gap-0 border border-ink">
              <div className="col-span-12 md:col-span-8 border-r-0 md:border-r border-b md:border-b-0 border-ink p-6">
                <div className="label-uppercase mb-3">
                  <span className="bg-editorial-red text-newsprint px-2 py-0.5 font-bold mr-2">BREAKING</span>
                  Trending Now
                </div>
                <TrendingTopics />
              </div>
              <div className="col-span-12 md:col-span-4 border-ink p-6">
                <div className="label-uppercase mb-3">Sentiment Index</div>
                <FakeRealChart />
              </div>
            </div>

            <div className="grid grid-cols-12 gap-0 border-l border-r border-b border-ink">
              <div className="col-span-12 md:col-span-5 border-r-0 md:border-r border-b md:border-b-0 border-ink p-6">
                <div className="label-uppercase mb-3">Sentiment Timeline</div>
                <SentimentTimeline />
              </div>
              <div className="col-span-12 md:col-span-7 p-6">
                <div className="label-uppercase mb-3">Live Wire</div>
                <LiveFeed />
              </div>
            </div>

            <div className="ornament-divider">&#x2727; &#x2727; &#x2727;</div>
          </div>
        )}

        {activeTab === "deepdive" && (
          <TopicDeepDive />
        )}

        {activeTab === "classify" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                The Fact Desk
              </h2>
              <p className="label-uppercase mt-2">
                Text Classification & Misinformation Detector
              </p>
            </div>
            <TextClassifier />
          </div>
        )}

        {activeTab === "trends" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Cluster Report
              </h2>
              <p className="label-uppercase mt-2">
                Topic Intelligence & Analysis
              </p>
            </div>
            <TopicClusters />
          </div>
        )}

        {activeTab === "compare" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Comparative Analysis
              </h2>
              <p className="label-uppercase mt-2">
                Side-by-Side Topic Intelligence
              </p>
            </div>
            <TopicComparison />
          </div>
        )}

        {activeTab === "sources" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Authority Index
              </h2>
              <p className="label-uppercase mt-2">
                Source Credibility & Trust Ratings
              </p>
            </div>
            <SourceScorecard />
          </div>
        )}

        {activeTab === "feed" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                The Wire
              </h2>
              <p className="label-uppercase mt-2">
                Live Intelligence Stream
              </p>
            </div>
            <LiveFeed fullView />
          </div>
        )}

        {activeTab === "explorer" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Post Bureau
              </h2>
              <p className="label-uppercase mt-2">
                Deep-Dive Content Explorer
              </p>
            </div>
            <PostExplorer />
          </div>
        )}

        {activeTab === "globe" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Global Desk
              </h2>
              <p className="label-uppercase mt-2">
                Worldwide Sentiment Distribution
              </p>
            </div>
            <div className="max-w-screen-xl mx-auto">
              {loadingGlobe ? (
                <div className="border border-ink p-12 text-center font-mono text-xs uppercase tracking-widest text-neutral-500">
                  <AlertTriangle className="h-6 w-6 mx-auto mb-3" strokeWidth={1.5} />
                  Loading globe data...
                </div>
              ) : (
                <GlobeView data={globeData} />
              )}
            </div>
          </div>
        )}

        {activeTab === "propagation" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Propagation Trail
              </h2>
              <p className="label-uppercase mt-2">
                Trace How Information Spreads
              </p>
            </div>
            <div className="max-w-screen-xl mx-auto space-y-4">
              <div className="flex gap-2 border border-ink p-4">
                <input
                  type="text"
                  value={propagationTopic}
                  onChange={(e) => setPropagationTopic(e.target.value)}
                  placeholder="Enter topic (e.g., mental health)"
                  className="flex-1 newsprint-input"
                  style={{ borderRadius: 0 }}
                />
                <button
                  onClick={() => loadPropagation(propagationTopic)}
                  className="btn-primary"
                >
                  Trace
                </button>
              </div>
              {loadingProp ? (
                <div className="border border-ink p-12 text-center font-mono text-xs uppercase tracking-widest text-neutral-500">
                  Tracing propagation...
                </div>
              ) : (
                <PropagationGraph data={propagationData} />
              )}
            </div>
          </div>
        )}

        {activeTab === "export" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Press Room
              </h2>
              <p className="label-uppercase mt-2">
                Export & Download Reports
              </p>
            </div>
            <ReportExport />
          </div>
        )}

        {activeTab === "profile" && (
          <div>
            <div className="border-b-4 border-ink pb-2 mb-8">
              <h2 className="font-serif text-4xl lg:text-5xl font-black leading-[0.9] tracking-tighter">
                Your Desk
              </h2>
              <p className="label-uppercase mt-2">
                Account & Personal Dashboard
              </p>
            </div>
            {user ? <UserDashboard /> : <AuthForm />}
          </div>
        )}
      </main>

      <footer className="border-t-4 border-ink bg-ink text-newsprint mt-16">
        <div className="max-w-screen-xl mx-auto px-4 py-8">
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 md:col-span-5">
              <h3 className="font-serif text-2xl font-bold tracking-tighter">
                SOCIAL<span className="text-editorial-red">PULSE</span>
              </h3>
              <p className="font-body text-neutral-400 text-sm mt-2 leading-relaxed">
                ML-powered platform for detecting hot topics, analyzing sentiment,
                and identifying misinformation in real-time across social media.
              </p>
            </div>
            <div className="col-span-6 md:col-span-2">
              <div className="label-uppercase text-neutral-400 mb-3">Sections</div>
              <div className="space-y-2">
                {TABS.slice(0, 5).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    className="block text-xs font-sans text-neutral-400 hover:text-newsprint transition-colors duration-200 uppercase tracking-wider"
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="col-span-6 md:col-span-2">
              <div className="label-uppercase text-neutral-400 mb-3">Analysis</div>
              <div className="space-y-2">
                {TABS.slice(5).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    className="block text-xs font-sans text-neutral-400 hover:text-newsprint transition-colors duration-200 uppercase tracking-wider"
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="col-span-12 md:col-span-3">
              <div className="label-uppercase text-neutral-400 mb-3">Edition</div>
              <p className="font-mono text-xs text-neutral-500">
                Edition: Vol 1.0<br />
                Printed in New York<br />
                {today}
              </p>
            </div>
          </div>
          <div className="border-t border-neutral-700 mt-8 pt-4 text-center font-mono text-xs text-neutral-500">
            &copy; {new Date().getFullYear()} SocialPulse AI. All rights reserved.
          </div>
        </div>
      </footer>
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