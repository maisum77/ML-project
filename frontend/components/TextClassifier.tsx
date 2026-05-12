"use client";

import { useState } from "react";
import { classifyText, getOverallSentiment } from "../lib/api";

interface LinguisticFlag {
  flag: string;
  count: number;
  score: number;
}

interface EntityExtraction {
  people: string[];
  organizations: string[];
  locations: string[];
}

interface TopicDetection {
  topic: string;
  relevance: number;
}

interface FactCheckResult {
  claims_checked: number;
  matches: { claim_text: string; verdict: string; publisher: string }[];
  claimbuster_available: boolean;
  google_fact_check_available: boolean;
  claimbuster_score?: number;
  checkworthy?: boolean;
  verdict: string;
}

interface DetailedAnalysis {
  sentiment: { label: string; score: number; model: string };
  credibility: { label: string; confidence: number; risk_level: string };
  linguistic_signals: { score: number; flags: LinguisticFlag[]; word_count: number; avg_sentence_length: number };
  emotional_analysis: { primary_emotion: string; emotion_scores: Record<string, number>; subjectivity: number; emotional_intensity: number };
  source_analysis: { source_type: string; authority_score: number; domains: string[]; has_attribution: boolean; has_quotes: boolean; attribution_score: number };
  entity_extraction: EntityExtraction;
  topic_detection: TopicDetection[];
  fact_check_results: FactCheckResult;
}

interface ClassifyResult {
  text: string;
  analysis: DetailedAnalysis;
  verdict: { label: string; confidence: number; risk_level: string; explanation: string; signal_weights: Record<string, number> };
  source: string | null;
  model_version: string;
}

function RiskBadge({ level }: { level: string }) {
  const styles: Record<string, string> = {
    high: "bg-red-100 text-red-800 border-red-300",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
    low: "bg-green-100 text-green-800 border-green-300",
  };
  return (
    <span className={`badge border ${styles[level] || styles.medium}`}>
      {level.toUpperCase()} RISK
    </span>
  );
}

function VerdictIcon({ label }: { label: string }) {
  if (label === "likely_reliable") return <span className="text-3xl">&#9989;</span>;
  if (label === "likely_unreliable") return <span className="text-3xl">&#10060;</span>;
  return <span className="text-3xl">&#9888;&#65039;</span>;
}

function SignalBar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct > 60 ? "bg-red-400" : pct > 30 ? "bg-yellow-400" : "bg-green-400";
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>{label}</span>
        <span>{value.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function TextClassifier() {
  const [text, setText] = useState("");
  const [source, setSource] = useState("");
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClassify = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/classify/detailed`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: text.trim(), source: source.trim() || null }),
        }
      );
      if (!res.ok) throw new Error("Classification failed");
      setResult(await res.json());
    } catch (err: any) {
      setError(err.message || "Failed to classify text");
    } finally {
      setLoading(false);
    }
  };

  const sampleTexts = [
    { label: "Fake News Sample", text: "SHOCKING: Doctors HATE this one weird trick! Big Pharma doesn't want you to know this MIRACLE cure that's 100% GUARANTEED!!" },
    { label: "Credible Sample", text: "According to a study published in The Lancet, WHO researchers found that regular exercise reduces the risk of heart disease by up to 30 percent." },
    { label: "Political Claim", text: "Breaking: New legislation proposed in Congress aims to address climate change through carbon pricing and renewable energy incentives." },
  ];

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Text Classification & Misinformation Detector</h2>
        <p className="text-gray-500 text-sm mb-4">
          Paste any text to analyze its credibility, sentiment, emotional language, topic relevance, and fact-check status.
        </p>

        <div className="mb-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">Text to Analyze</label>
          <textarea
            className="w-full border rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={4}
            placeholder="Enter a news article, social media post, or any text to analyze..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Source (optional)</label>
          <input
            type="text"
            className="w-full border rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., @WHO, cnn.com, reddit/r/science"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleClassify}
            disabled={loading || !text.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Analyzing..." : "Analyze Text"}
          </button>
          <span className="text-xs text-gray-400">Try a sample:</span>
          {sampleTexts.map((s) => (
            <button
              key={s.label}
              onClick={() => { setText(s.text); setSource(""); }}
              className="text-xs text-blue-600 hover:underline"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">{error}</div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Verdict Card */}
          <div className={`card border-l-4 ${
            result.verdict.risk_level === "high" ? "border-l-red-500 bg-red-50" :
            result.verdict.risk_level === "medium" ? "border-l-yellow-500 bg-yellow-50" :
            "border-l-green-500 bg-green-50"
          }`}>
            <div className="flex items-center gap-4">
              <VerdictIcon label={result.verdict.label} />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-lg font-semibold capitalize">
                    {result.verdict.label.replace(/_/g, " ")}
                  </h3>
                  <RiskBadge level={result.verdict.risk_level} />
                </div>
                <p className="text-gray-700 text-sm">{result.verdict.explanation}</p>
                <p className="text-gray-500 text-xs mt-1">Confidence: {result.verdict.confidence}%</p>
              </div>
            </div>
          </div>

          {/* Analysis Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sentiment */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Sentiment</h3>
              <div className="flex items-center gap-3 mb-2">
                <span className={`badge ${result.analysis.sentiment.label === "positive" ? "badge-positive" : result.analysis.sentiment.label === "negative" ? "badge-negative" : "badge-neutral"}`}>
                  {result.analysis.sentiment.label}
                </span>
                <span className="text-gray-600 text-sm">Score: {result.analysis.sentiment.score}%</span>
              </div>
              <div className="text-xs text-gray-400">Model: {result.analysis.sentiment.model}</div>
            </div>

            {/* Credibility */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Credibility</h3>
              <div className="flex items-center gap-3 mb-2">
                <RiskBadge level={result.analysis.credibility.risk_level} />
                <span className="text-gray-600 text-sm">Confidence: {result.analysis.credibility.confidence}%</span>
              </div>
              <div className="text-sm text-gray-500 capitalize">{result.analysis.credibility.label.replace(/_/g, " ")}</div>
            </div>

            {/* Linguistic Signals */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Linguistic Analysis</h3>
              <SignalBar label="Sensationalism Score" value={result.analysis.linguistic_signals.score} />
              {result.analysis.linguistic_signals.flags.length > 0 ? (
                <div className="space-y-1">
                  {result.analysis.linguistic_signals.flags.map((f, i) => (
                    <div key={i} className="flex justify-between text-xs">
                      <span className="text-gray-700">{f.flag.replace(/_/g, " ")}</span>
                      <span className="text-red-600">+{f.score} ({f.count}x)</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-green-600 text-sm">No suspicious patterns detected</p>
              )}
              <div className="mt-2 text-xs text-gray-400">
                {result.analysis.linguistic_signals.word_count} words &middot; avg {result.analysis.linguistic_signals.avg_sentence_length} words/sentence
              </div>
            </div>

            {/* Emotional Analysis */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Emotional Language</h3>
              <div className="mb-2">
                <span className="text-sm font-medium capitalize">{result.analysis.emotional_analysis.primary_emotion}</span>
                <span className="text-gray-500 text-sm ml-2">
                  Subjectivity: {(result.analysis.emotional_analysis.subjectivity * 100).toFixed(0)}%
                </span>
              </div>
              {Object.keys(result.analysis.emotional_analysis.emotion_scores).length > 0 ? (
                <div className="space-y-1">
                  {Object.entries(result.analysis.emotional_analysis.emotion_scores).map(([emo, count]) => (
                    <div key={emo} className="flex justify-between text-xs">
                      <span className="capitalize">{emo}</span>
                      <span>{count} word{count > 1 ? "s" : ""}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No strong emotional language detected</p>
              )}
              <SignalBar label="Emotional Intensity" value={result.analysis.emotional_analysis.emotional_intensity} />
            </div>

            {/* Source Analysis */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Source Analysis</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Source Type</span>
                  <span className="font-medium capitalize">{result.analysis.source_analysis.source_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Authority Score</span>
                  <span className="font-medium">{result.analysis.source_analysis.authority_score}/100</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Attribution</span>
                  <span className="font-medium">{result.analysis.source_analysis.has_attribution ? "Present" : "None"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Quotes</span>
                  <span className="font-medium">{result.analysis.source_analysis.has_quotes ? "Present" : "None"}</span>
                </div>
                <SignalBar label="Attribution Score" value={result.analysis.source_analysis.attribution_score} />
              </div>
            </div>

            {/* Facts & Topics */}
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Fact-Check & Topics</h3>
              <div className="mb-3">
                <div className="text-xs text-gray-500 mb-1">Fact-Check Status</div>
                {result.analysis.fact_check_results.claims_checked > 0 ? (
                  <div className="space-y-2">
                    {result.analysis.fact_check_results.matches.map((m, i) => (
                      <div key={i} className="bg-gray-50 rounded p-2 text-xs">
                        <div className="font-medium">{m.verdict}</div>
                        <div className="text-gray-500">{m.publisher}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">
                    {result.analysis.fact_check_results.google_fact_check_available ? "No matching claims found" : "Fact-check API unavailable"}
                  </div>
                )}
                {result.analysis.fact_check_results.claimbuster_available && result.analysis.fact_check_results.claimbuster_score !== undefined && (
                  <div className="mt-2 text-xs text-gray-500">
                    Checkworthiness score: {(result.analysis.fact_check_results.claimbuster_score * 100).toFixed(0)}%
                  </div>
                )}
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Detected Topics</div>
                {result.analysis.topic_detection.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.analysis.topic_detection.map((t, i) => (
                      <span key={i} className="badge bg-blue-100 text-blue-800">
                        {t.topic} ({t.relevance.toFixed(0)}%)
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-sm text-gray-400">No topics detected</span>
                )}
              </div>
            </div>
          </div>

          {/* Signal Weights */}
          <div className="card">
            <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Analysis Breakdown</h3>
            <div className="space-y-2">
              <SignalBar label="Linguistic Signals" value={result.verdict.signal_weights.linguistic * 100} />
              <SignalBar label="Emotional Language" value={result.verdict.signal_weights.emotional * 100} />
              <SignalBar label="Source Reliability" value={result.verdict.signal_weights.source_reliability * 100} />
              <SignalBar label="Fact-Check Risk" value={result.verdict.signal_weights.fact_check_risk * 100} />
              <SignalBar label="Sentiment Extremity" value={result.verdict.signal_weights.sentiment_extremity * 100} />
            </div>
          </div>

          {/* Entities */}
          {((result.analysis.entity_extraction.people?.length || 0) +
            (result.analysis.entity_extraction.organizations?.length || 0) +
            (result.analysis.entity_extraction.locations?.length || 0)) > 0 && (
            <div className="card">
              <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-gray-500">Entity Extraction</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-gray-500 mb-1">People</div>
                  {result.analysis.entity_extraction.people.length > 0 ? (
                    result.analysis.entity_extraction.people.map((p, i) => (
                      <span key={i} className="badge bg-purple-100 text-purple-800 mr-1">{p}</span>
                    ))
                  ) : <span className="text-xs text-gray-400">None detected</span>}
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Organizations</div>
                  {result.analysis.entity_extraction.organizations.length > 0 ? (
                    result.analysis.entity_extraction.organizations.map((o, i) => (
                      <span key={i} className="badge bg-blue-100 text-blue-800 mr-1">{o}</span>
                    ))
                  ) : <span className="text-xs text-gray-400">None detected</span>}
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Locations</div>
                  {result.analysis.entity_extraction.locations.length > 0 ? (
                    result.analysis.entity_extraction.locations.map((l, i) => (
                      <span key={i} className="badge bg-green-100 text-green-800 mr-1">{l}</span>
                    ))
                  ) : <span className="text-xs text-gray-400">None detected</span>}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}