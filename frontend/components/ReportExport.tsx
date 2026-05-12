"use client";

import { useState } from "react";

export default function ReportExport() {
  const [loading, setLoading] = useState(false);
  const [platform, setPlatform] = useState("");

  const downloadReport = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (platform) params.set("platform", platform);
      const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/export/report?${params}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to generate report");
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `socialpulse-report-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
    } catch (err: any) {
      alert("Failed to export report: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-3">Export Analysis Report</h2>
      <p className="text-sm text-gray-500 mb-4">
        Download a comprehensive text report of all analysis data, including sentiment distribution, authority breakdown, and topic clusters.
      </p>
      <div className="flex gap-3 items-end">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Platform filter (optional)</label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="border rounded px-3 py-2 text-sm"
          >
            <option value="">All platforms</option>
            <option value="twitter">Twitter/X</option>
            <option value="reddit">Reddit</option>
          </select>
        </div>
        <button
          onClick={downloadReport}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Download Report"}
        </button>
      </div>
    </div>
  );
}