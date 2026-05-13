"use client";

import { useState, useEffect } from "react";
import { Search, Filter } from "lucide-react";

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

  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading authority scorecard...</div>;
  if (!data) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500">No authority data available</div>;

  const filtered = data.sources.filter((s) => {
    const matchesFilter = filter === "all" || s.type === filter;
    const matchesSearch = search === "" || s.handle.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const stats = [
    { label: "Tracked Sources", value: data.total_sources },
    { label: "Twitter/X Sources", value: data.twitter_sources },
    { label: "Reddit Sources", value: data.reddit_sources },
    { label: "Authority Domains", value: data.authority_domains },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-12 gap-0 border border-ink">
        {stats.map((stat, i) => (
          <div key={stat.label} className={`col-span-6 md:col-span-3 p-6 border-b md:border-b-0 border-ink ${
            i < stats.length - 1 ? "border-r-0 md:border-r" : ""
          }`}>
            <div className="label-uppercase text-neutral-400 mb-2">{stat.label}</div>
            <div className="font-serif text-3xl lg:text-5xl font-black tracking-tighter">{stat.value}</div>
          </div>
        ))}
      </div>

      {Object.keys(data.type_distribution).length > 0 && (
        <div className="border border-ink p-6">
          <div className="label-uppercase mb-4">Source Type Distribution</div>
          <div className="flex flex-wrap gap-3">
            {Object.entries(data.type_distribution).map(([type, count]) => (
              <div key={type} className="border border-ink px-3 py-2 flex items-center gap-2">
                <span className="font-sans text-xs uppercase tracking-widest font-semibold">{type}</span>
                <span className="font-mono text-lg font-bold">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="border border-ink">
        <div className="p-6 border-b border-ink">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" strokeWidth={1.5} />
              <input
                type="text"
                placeholder="Search sources..."
                className="w-full newsprint-input pl-10"
                style={{ borderRadius: 0 }}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              {["all", "official", "journalist"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 font-sans text-xs uppercase tracking-widest font-semibold transition-all duration-200 min-h-[44px] ${
                    filter === f
                      ? "bg-ink text-newsprint"
                      : "border border-ink hover:bg-ink hover:text-newsprint"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-4 border-ink">
                <th className="py-3 px-6 text-left label-uppercase">Source</th>
                <th className="py-3 px-6 text-left label-uppercase">Platform</th>
                <th className="py-3 px-6 text-left label-uppercase">Type</th>
                <th className="py-3 px-6 text-left label-uppercase">Authority</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 50).map((source, i) => (
                <tr key={i} className="border-b border-ink hover:bg-neutral-100 transition-colors duration-200">
                  <td className="py-3 px-6 font-serif font-bold">{source.handle}</td>
                  <td className="py-3 px-6">
                    <span className="font-sans text-xs uppercase tracking-widest">{source.platform}</span>
                  </td>
                  <td className="py-3 px-6">
                    <span className="border border-ink px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest">
                      {source.type}
                    </span>
                  </td>
                  <td className="py-3 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-20 h-2 bg-newsprint-muted">
                        <div
                          className={`h-2 ${
                            source.authority_score >= 80 ? "bg-ink" :
                            source.authority_score >= 60 ? "bg-neutral-500" : "bg-editorial-red"
                          }`}
                          style={{ width: `${source.authority_score}%` }}
                        />
                      </div>
                      <span className="font-mono text-sm font-bold">{source.authority_score}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length > 50 && (
            <div className="p-4 font-mono text-xs text-neutral-400 uppercase tracking-widest text-center border-t border-ink">
              Showing 50 of {filtered.length} sources
            </div>
          )}
        </div>
      </div>

      {data.domains.length > 0 && (
        <div className="border border-ink p-6">
          <div className="label-uppercase mb-4">Authority Domains</div>
          <div className="flex flex-wrap gap-2">
            {data.domains.map((d, i) => (
              <span
                key={i}
                className="border border-ink px-3 py-1 font-mono text-xs hover:bg-ink hover:text-newsprint transition-colors duration-200 cursor-default"
              >
                {d.domain}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}