"use client";

import { useState, useEffect } from "react";

interface Source {
  handle: string;
  platform: string;
  type: string;
  authority_score: number;
}

interface Domain {
  domain: string;
  type: string;
}

interface ScorecardData {
  total_sources: number;
  twitter_sources: number;
  reddit_sources: number;
  authority_domains: number;
  type_distribution: Record<string, number>;
  sources: Source[];
  domains: Domain[];
}

export default function SourceScorecard() {
  const [data, setData] = useState<ScorecardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchScorecard = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/authority/scorecard`
        );
        if (res.ok) setData(await res.json());
      } catch (err) {
        console.error("Failed to fetch scorecard:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchScorecard();
  }, []);

  if (loading) return <div className="card">Loading authority scorecard...</div>;
  if (!data) return <div className="card text-gray-500">No authority data available</div>;

  const filtered = data.sources.filter((s) => {
    const matchesFilter = filter === "all" || s.type === filter;
    const matchesSearch = search === "" || s.handle.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const typeColor: Record<string, string> = {
    official: "bg-blue-100 text-blue-800",
    journalist: "bg-purple-100 text-purple-800",
    org: "bg-green-100 text-green-800",
    government: "bg-red-100 text-red-800",
    academic: "bg-yellow-100 text-yellow-800",
    organization: "bg-green-100 text-green-800",
  };

  const platformIcon: Record<string, string> = {
    twitter: "\uD83D\uDC26",
    reddit: "\uD83D\uDCC4",
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600">{data.total_sources}</div>
          <div className="text-sm text-gray-500 mt-1">Tracked Sources</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-sky-600">{data.twitter_sources}</div>
          <div className="text-sm text-gray-500 mt-1">Twitter/X Sources</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-orange-600">{data.reddit_sources}</div>
          <div className="text-sm text-gray-500 mt-1">Reddit Sources</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600">{data.authority_domains}</div>
          <div className="text-sm text-gray-500 mt-1">Authority Domains</div>
        </div>
      </div>

      {/* Type Distribution */}
      <div className="card">
        <h3 className="font-semibold mb-3">Source Type Distribution</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(data.type_distribution).map(([type, count]) => (
            <div key={type} className="flex items-center gap-2">
              <span className={`badge ${typeColor[type] || "badge-neutral"}`}>
                {type}
              </span>
              <span className="text-sm text-gray-600">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Search and Filter */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-3 mb-4">
          <input
            type="text"
            placeholder="Search sources..."
            className="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="flex gap-2">
            {["all", "official", "journalist"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-sm capitalize transition ${
                  filter === f
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Source Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-2 pr-4">Source</th>
                <th className="pb-2 pr-4">Platform</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2">Authority</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 50).map((source, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2 pr-4 font-medium">{source.handle}</td>
                  <td className="py-2 pr-4">
                    <span className="text-lg mr-1">{platformIcon[source.platform]}</span>
                    <span className="capitalize text-gray-600">{source.platform}</span>
                  </td>
                  <td className="py-2 pr-4">
                    <span className={`badge ${typeColor[source.type] || "badge-neutral"}`}>
                      {source.type}
                    </span>
                  </td>
                  <td className="py-2">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            source.authority_score >= 80 ? "bg-green-500" :
                            source.authority_score >= 60 ? "bg-yellow-500" : "bg-red-500"
                          }`}
                          style={{ width: `${source.authority_score}%` }}
                        />
                      </div>
                      <span className="text-gray-600">{source.authority_score}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length > 50 && (
            <p className="text-gray-400 text-xs mt-2">Showing 50 of {filtered.length} sources</p>
          )}
        </div>
      </div>

      {/* Authority Domains */}
      <div className="card">
        <h3 className="font-semibold mb-3">Authority Domains</h3>
        <div className="flex flex-wrap gap-2">
          {data.domains.map((d, i) => (
            <span
              key={i}
              className={`badge ${typeColor[d.type] || "badge-neutral"}`}
            >
              {d.domain}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}