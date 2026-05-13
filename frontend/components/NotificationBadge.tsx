"use client";

import { useState, useEffect, useCallback } from "react";
import { Bell } from "lucide-react";

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
        className="relative p-2 border border-ink min-h-[44px] min-w-[44px] flex items-center justify-center hover:bg-ink hover:text-newsprint transition-all duration-200"
        title="Notifications"
      >
        <Bell className="h-5 w-5" strokeWidth={1.5} />
        {count > 0 && (
          <span className="absolute -top-1 -right-1 bg-editorial-red text-newsprint font-sans text-[10px] font-bold w-5 h-5 flex items-center justify-center">
            {count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 w-80 bg-newsprint border border-ink z-50 shadow-hard">
          <div className="p-4 border-b-4 border-ink font-serif font-bold">
            Keyword Alerts
          </div>
          {data && data.matches.length > 0 ? (
            <div className="max-h-64 overflow-y-auto scrollbar-hide">
              {data.matches.map((m) => (
                <div key={m.keyword} className="px-4 py-3 border-b border-ink hover:bg-neutral-100 transition-colors duration-200">
                  <div className="flex items-center gap-2">
                    <span className="bg-editorial-red text-newsprint px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold">
                      {m.keyword}
                    </span>
                    <span className="font-mono text-xs text-neutral-400">{m.count} new post{m.count !== 1 ? "s" : ""}</span>
                  </div>
                  <p className="font-body text-xs text-neutral-600 mt-1 truncate">{m.latest_title}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center font-mono text-xs uppercase tracking-widest text-neutral-400">
              No keyword alerts triggered. Add alerts in your Profile.
            </div>
          )}
          <div className="p-3 border-t border-ink text-center">
            <button
              onClick={() => { fetchNotifications(); setOpen(false); }}
              className="btn-ghost inline-block"
            >
              Refresh
            </button>
          </div>
        </div>
      )}
    </div>
  );
}