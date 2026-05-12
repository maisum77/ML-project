"use client";

import { useState, useEffect } from "react";
import { useAuth } from "../lib/auth";

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
  if (loading) return <div className="card">Loading dashboard...</div>;

  return (
    <div className="space-y-6">
      {/* Profile Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">{user.username}</h2>
            <p className="text-gray-500 text-sm">{user.email}</p>
          </div>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-red-600">
            Sign Out
          </button>
        </div>
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-blue-600">{savedAnalyses.length}</div>
            <div className="text-xs text-gray-500">Saved Analyses</div>
          </div>
          <div className="bg-orange-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-orange-600">{keywordAlerts.length}</div>
            <div className="text-xs text-gray-500">Keyword Alerts</div>
          </div>
        </div>
      </div>

      {/* Keyword Alerts */}
      <div className="card">
        <h3 className="font-semibold mb-3">Keyword Alerts</h3>
        <p className="text-gray-500 text-xs mb-3">
          Set keywords to monitor. When trending topics match, they will be highlighted.
        </p>
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addAlert()}
            placeholder="Add a keyword (e.g., AI, vaccine, climate)"
            className="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          />
          <button onClick={addAlert} className="btn-primary text-sm">
            Add
          </button>
        </div>
        {keywordAlerts.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywordAlerts.map((kw) => (
              <span
                key={kw}
                className="badge bg-orange-100 text-orange-800 cursor-pointer hover:bg-orange-200"
                onClick={() => removeAlert(kw)}
                title="Click to remove"
              >
                {kw} &times;
              </span>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No alerts set. Add keywords above.</p>
        )}
      </div>

      {/* Saved Analyses */}
      <div className="card">
        <h3 className="font-semibold mb-3">Saved Analyses</h3>
        {savedAnalyses.length > 0 ? (
          <div className="space-y-3">
            {savedAnalyses.map((analysis, i) => (
              <div key={i} className="border rounded-lg p-3 hover:bg-gray-50">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-sm">
                    {analysis.data?.topic || analysis.data?.text?.substring(0, 40) || `Analysis #${i + 1}`}
                  </span>
                  <span className="text-xs text-gray-400">
                    {analysis.saved_at ? new Date(analysis.saved_at).toLocaleDateString() : ""}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">
            No saved analyses yet. Classify text and save results to see them here.
          </p>
        )}
      </div>
    </div>
  );
}