"use client";

import { useState, useEffect } from "react";
import { useAuth } from "../lib/auth";
import { LogOut, Bell, Plus, X } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UserDashboard() {
  const { user, token, logout } = useAuth();
  const [savedAnalyses, setSavedAnalyses] = useState<any[]>([]);
  const [keywordAlerts, setKeywordAlerts] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    fetchUserData();
  }, [token]);

  const fetchUserData = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setSavedAnalyses(data.saved_analyses || []);
        setKeywordAlerts(data.keyword_alerts || []);
      }
    } catch (err) {
      console.error("Failed to fetch user data:", err);
    } finally {
      setLoading(false);
    }
  };

  const addAlert = async () => {
    if (!newKeyword.trim() || !token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/alerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ keyword: newKeyword.trim() }),
      });
      if (res.ok) {
        setKeywordAlerts([...keywordAlerts, newKeyword.trim()]);
        setNewKeyword("");
      }
    } catch (err) {
      console.error("Failed to add alert:", err);
    }
  };

  const removeAlert = async (keyword: string) => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/alerts/${encodeURIComponent(keyword)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setKeywordAlerts(keywordAlerts.filter((k) => k !== keyword));
      }
    } catch (err) {
      console.error("Failed to remove alert:", err);
    }
  };

  if (!user) return null;
  if (loading) return <div className="font-mono text-xs uppercase tracking-widest text-neutral-500 py-4">Loading dashboard...</div>;

  const today = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="space-y-6">
      <div className="border border-ink p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-serif text-3xl font-black tracking-tighter">{user.username}</h2>
            <p className="font-mono text-xs text-neutral-400 uppercase tracking-widest mt-1">{user.email}</p>
          </div>
          <button onClick={logout} className="btn-secondary inline-flex items-center gap-2">
            <LogOut className="h-4 w-4" strokeWidth={1.5} />
            Sign Out
          </button>
        </div>
        <div className="grid grid-cols-12 gap-0 border border-ink">
          <div className="col-span-6 border-r border-b border-ink p-6 text-center">
            <div className="font-serif text-4xl font-black tracking-tighter">{savedAnalyses.length}</div>
            <div className="label-uppercase mt-1">Saved Analyses</div>
          </div>
          <div className="col-span-6 border-b border-ink p-6 text-center">
            <div className="font-serif text-4xl font-black tracking-tighter">{keywordAlerts.length}</div>
            <div className="label-uppercase mt-1">Keyword Alerts</div>
          </div>
        </div>
      </div>

      <div className="border border-ink p-6">
        <div className="flex items-center gap-3 mb-4">
          <Bell className="h-5 w-5 text-ink" strokeWidth={1.5} />
          <h3 className="font-serif text-xl font-black">Keyword Alerts</h3>
        </div>
        <p className="font-body text-neutral-500 text-xs mb-4">
          Set keywords to monitor. When trending topics match, they will be highlighted.
        </p>
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addAlert()}
            placeholder="Add a keyword (e.g., AI, vaccine, climate)"
            className="flex-1 newsprint-input"
            style={{ borderRadius: 0 }}
          />
          <button onClick={addAlert} className="btn-primary inline-flex items-center gap-2">
            <Plus className="h-4 w-4" strokeWidth={1.5} />
            Add
          </button>
        </div>
        {keywordAlerts.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywordAlerts.map((kw) => (
              <span
                key={kw}
                className="border border-ink px-3 py-1.5 font-mono text-xs inline-flex items-center gap-2 cursor-pointer hover:bg-editorial-red hover:text-newsprint hover:border-editorial-red transition-colors duration-200 group"
                onClick={() => removeAlert(kw)}
                title="Click to remove"
              >
                {kw}
                <X className="h-3 w-3 opacity-0 group-hover:opacity-100" strokeWidth={1.5} />
              </span>
            ))}
          </div>
        ) : (
          <p className="font-mono text-xs uppercase tracking-widest text-neutral-400">No alerts set. Add keywords above.</p>
        )}
      </div>

      <div className="border border-ink p-6">
        <h3 className="font-serif text-xl font-black mb-4">Saved Analyses</h3>
        {savedAnalyses.length > 0 ? (
          <div className="divide-y divide-ink">
            {savedAnalyses.map((analysis, i) => (
              <div key={i} className="py-3 hover:bg-neutral-100 transition-colors duration-200 px-2 -mx-2">
                <div className="flex justify-between items-center">
                  <span className="font-serif font-bold text-sm">
                    {analysis.data?.topic || analysis.data?.text?.substring(0, 40) || `Analysis #${i + 1}`}
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-neutral-400">
                    {analysis.saved_at ? new Date(analysis.saved_at).toLocaleDateString() : ""}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="font-mono text-xs uppercase tracking-widest text-neutral-400">
            No saved analyses yet. Classify text and save results to see them here.
          </p>
        )}
      </div>
    </div>
  );
}