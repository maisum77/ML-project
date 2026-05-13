"use client";

import { useState } from "react";
import { Download, FileText } from "lucide-react";

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
    <div className="border border-ink p-8">
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-12 md:col-span-7">
          <h3 className="font-serif text-2xl font-black mb-4">
            Comprehensive Analysis Report
          </h3>
          <p className="font-body text-neutral-600 text-sm leading-relaxed drop-cap">
            Download a comprehensive text report of all analysis data, including sentiment distribution, authority breakdown, and topic clusters. The report is generated in real-time and includes the most current data available.
          </p>
          <div className="mt-6 border-t-4 border-ink pt-6">
            <div className="flex gap-3 items-end">
              <div>
                <label className="label-uppercase block mb-2">Platform filter (optional)</label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="newsprint-input"
                  style={{ borderRadius: 0 }}
                >
                  <option value="">All platforms</option>
                  <option value="twitter">Twitter/X</option>
                  <option value="reddit">Reddit</option>
                </select>
              </div>
              <button
                onClick={downloadReport}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                <Download className="h-4 w-4" strokeWidth={1.5} />
                {loading ? "Generating..." : "Download Report"}
              </button>
            </div>
          </div>
        </div>
        <div className="col-span-12 md:col-span-5 flex items-center justify-center">
          <div className="border-4 border-ink p-8 text-center">
            <FileText className="h-16 w-16 mx-auto mb-4 text-neutral-400" strokeWidth={0.5} />
            <div className="label-uppercase text-neutral-400 mb-1">Format</div>
            <div className="font-serif text-xl font-black">Plain Text</div>
            <div className="font-mono text-xs text-neutral-400 mt-1">.txt</div>
          </div>
        </div>
      </div>
    </div>
  );
}