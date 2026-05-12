"use client";

import { useState, useEffect, useCallback } from "react";

interface Match {
  keyword: string;
  count: number;
  latest_title: string;
}

interface NotificationData {
  count: number;
  matches: Match[];
}

export default function NotificationBadge() {
  const [data, setData] = useState<NotificationData | null>(null);
  const [open, setOpen] = useState(false);

  const token = typeof window !== "undefined" ? localStorage.getItem("socialpulse_token") : null;

  const fetchNotifications = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/notifications`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch {}
  }, [token]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  if (!token) return null;

  const count = data?.count ?? 0;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition"
        title="Notifications"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {count > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center font-bold">
            {count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-10 w-80 bg-white border rounded-lg shadow-lg z-50">
          <div className="p-3 border-b font-semibold text-sm">Keyword Alerts</div>
          {data && data.matches.length > 0 ? (
            <div className="max-h-64 overflow-y-auto">
              {data.matches.map((m) => (
                <div key={m.keyword} className="px-3 py-2 border-b hover:bg-gray-50">
                  <div className="flex items-center gap-2">
                    <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-medium">
                      {m.keyword}
                    </span>
                    <span className="text-xs text-gray-500">{m.count} new post{m.count !== 1 ? "s" : ""}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1 truncate">{m.latest_title}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 text-center text-sm text-gray-400">
              No keyword alerts triggered. Add alerts in your Profile.
            </div>
          )}
          <div className="p-2 border-t text-center">
            <button
              onClick={() => { fetchNotifications(); setOpen(false); }}
              className="text-xs text-blue-600 hover:underline"
            >
              Refresh
            </button>
          </div>
        </div>
      )}
    </div>
  );
}