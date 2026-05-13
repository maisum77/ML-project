"use client";

import { useState } from "react";
import { getOverallSentiment } from "../lib/api";
import { AlertTriangle, CheckCircle, XCircle, HelpCircle } from "lucide-react";

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
    high: "bg-editorial-red text-newsprint",
    medium: "border-2 border-ink",
    low: "bg-ink text-newsprint",
  };
  return (
    <span className={`px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold ${styles[level] || styles.medium}`}>
      {level.toUpperCase()} RISK
    </span>
  );
}

function VerdictIcon({ label }: { label: string }) {
  if (label === "likely_reliable") return <CheckCircle className="h-8 w-8 text-ink" strokeWidth={1.5} />;
  if (label === "likely_unreliable") return <XCircle className="h-8 w-8 text-editorial-red" strokeWidth={1.5} />;
  return <AlertTriangle className="h-8 w-8 text-neutral-500" strokeWidth={1.5} />;
}

function SignalBar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct > 60 ? "bg-editorial-red" : pct > 30 ? "bg-neutral-500" : "bg-ink";
  return (
    <div className="mb-2">
      <div className="flex justify-between font-mono text-xs mb-1">
        <span className="uppercase tracking-widest text-neutral-500">{label}</span>
        <span className="font-semibold">{value.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-newsprint-muted h-2">
        <div className={`${color} h-2 transition-all`} style={{ width: `${pct}%` }} />
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
      <div className="border border-ink p-6 bg-newsprint">
        <p className="font-body text-neutral-600 text-sm mb-6 drop-cap">
          Paste any text to analyze its credibility, sentiment, emotional language, topic relevance, and fact-check status.
        </p>

        <div className="mb-4">
          <label className="label-uppercase block mb-2">Text to Analyze</label>
          <textarea
            className="w-full border-b-2 border-ink bg-transparent px-3 py-2 font-body text-sm focus-visible:bg-neutral-100 focus-visible:outline-none min-h-[120px]"
            style={{ borderRadius: 0 }}
            placeholder="Enter a news article, social media post, or any text to analyze..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="label-uppercase block mb-2">Source (optional)</label>
          <input
            type="text"
            className="w-full newsprint-input"
            style={{ borderRadius: 0 }}
            placeholder="e.g., @WHO, cnn.com, reddit/r/science"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleClassify}
            disabled={loading || !text.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Analyzing..." : "Analyze Text"}
          </button>
          <span className="label-uppercase text-neutral-400">Try a sample:</span>
          {sampleTexts.map((s) => (
            <button
              key={s.label}
              onClick={() => { setText(s.text); setSource(""); }}
              className="text-xs font-sans text-ink underline-offset-4 decoration-2 decoration-editorial-red hover:underline uppercase tracking-widest"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="border-4 border-editorial-red bg-newsprint p-4 text-editorial-red font-mono text-xs">
          <AlertTriangle className="h-4 w-4 inline mr-2" strokeWidth={1.5} />
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className={`border-4 ${
            result.verdict.risk_level === "high" ? "border-editorial-red" :
            result.verdict.risk_level === "medium" ? "border-neutral-500" :
            "border-ink"
          } p-6 bg-newsprint`}>
            <div className="flex items-start gap-4">
              <VerdictIcon label={result.verdict.label} />
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-serif text-2xl font-black capitalize">
                    {result.verdict.label.replace(/_/g, " ")}
                  </h3>
                  <RiskBadge level={result.verdict.risk_level} />
                </div>
                <p className="font-body text-neutral-600">{result.verdict.explanation}</p>
                <p className="font-mono text-xs text-neutral-400 mt-1">Confidence: {result.verdict.confidence}%</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-0 border border-ink">
            <div className="col-span-12 md:col-span-6 border-r-0 md:border-r border-b md:border-b-0 border-ink p-6">
              <div className="label-uppercase mb-3">Sentiment</div>
              <div className="flex items-center gap-3 mb-2">
                <span className={`border px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest font-bold ${
                  result.analysis.sentiment.label === "positive" ? "border-ink bg-ink text-newsprint" :
                  result.analysis.sentiment.label === "negative" ? "border-editorial-red bg-editorial-red text-newsprint" :
                  "border-newsprint-muted text-neutral-600"
                }`}>
                  {result.analysis.sentiment.label}
                </span>
                <span className="font-mono text-sm">Score: {result.analysis.sentiment.score}%</span>
              </div>
              <div className="font-mono text-[10px] text-neutral-400 uppercase tracking-widest">
                Model: {result.analysis.sentiment.model}
              </div>
            </div>

            <div className="col-span-12 md:col-span-6 p-6">
              <div className="label-uppercase mb-3">Credibility</div>
              <div className="flex items-center gap-3 mb-2">
                <RiskBadge level={result.analysis.credibility.risk_level} />
                <span className="font-mono text-sm">Confidence: {result.analysis.credibility.confidence}%</span>
              </div>
              <div className="font-body text-sm text-neutral-600 capitalize">{result.analysis.credibility.label.replace(/_/g, " ")}</div>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-0 border-l border-r border-b border-ink">
            <div className="col-span-12 md:col-span-6 border-r-0 md:border-r border-b md:border-b-0 border-ink p-6">
              <div className="label-uppercase mb-3">Linguistic Analysis</div>
              <SignalBar label="Sensationalism Score" value={result.analysis.linguistic_signals.score} />
              {result.analysis.linguistic_signals.flags.length > 0 ? (
                <div className="space-y-1 mt-3">
                  {result.analysis.linguistic_signals.flags.map((f, i) => (
                    <div key={i} className="flex justify-between font-mono text-xs border-b border-newsprint-muted py-1">
                      <span className="uppercase tracking-widest">{f.flag.replace(/_/g, " ")}</span>
                      <span className="text-editorial-red font-bold">+{f.score} ({f.count}x)</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="font-mono text-xs uppercase tracking-widest text-ink">No suspicious patterns detected</p>
              )}
              <div className="mt-2 font-mono text-[10px] text-neutral-400 uppercase tracking-widest">
                {result.analysis.linguistic_signals.word_count} words &middot; avg {result.analysis.linguistic_signals.avg_sentence_length} words/sentence
              </div>
            </div>

            <div className="col-span-12 md:col-span-6 p-6">
              <div className="label-uppercase mb-3">Emotional Language</div>
              <div className="mb-2">
                <span className="font-serif font-bold capitalize">{result.analysis.emotional_analysis.primary_emotion}</span>
                <span className="font-mono text-xs text-neutral-500 ml-2">
                  Subjectivity: {(result.analysis.emotional_analysis.subjectivity * 100).toFixed(0)}%
                </span>
              </div>
              {Object.keys(result.analysis.emotional_analysis.emotion_scores).length > 0 ? (
                <div className="space-y-1">
                  {Object.entries(result.analysis.emotional_analysis.emotion_scores).map(([emo, count]) => (
                    <div key={emo} className="flex justify-between font-mono text-xs">
                      <span className="capitalize">{emo}</span>
                      <span>{count} word{count > 1 ? "s" : ""}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="font-body text-neutral-500 text-sm">No strong emotional language detected</p>
              )}
              <SignalBar label="Emotional Intensity" value={result.analysis.emotional_analysis.emotional_intensity} />
            </div>
          </div>

          <div className="grid grid-cols-12 gap-0 border-l border-r border-b border-ink">
            <div className="col-span-12 md:col-span-6 border-r-0 md:border-r border-b md:border-b-0 border-ink p-6">
              <div className="label-uppercase mb-3">Source Analysis</div>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-newsprint-muted py-2">
                  <span className="font-mono text-xs uppercase tracking-widest text-neutral-500">Source Type</span>
                  <span className="font-serif font-bold capitalize">{result.analysis.source_analysis.source_type}</span>
                </div>
                <div className="flex justify-between border-b border-newsprint-muted py-2">
                  <span className="font-mono text-xs uppercase tracking-widest text-neutral-500">Authority Score</span>
                  <span className="font-mono font-bold">{result.analysis.source_analysis.authority_score}/100</span>
                </div>
                <div className="flex justify-between border-b border-newsprint-muted py-2">
                  <span className="font-mono text-xs uppercase tracking-widest text-neutral-500">Attribution</span>
                  <span className="font-serif font-bold">{result.analysis.source_analysis.has_attribution ? "Present" : "None"}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="font-mono text-xs uppercase tracking-widest text-neutral-500">Quotes</span>
                  <span className="font-serif font-bold">{result.analysis.source_analysis.has_quotes ? "Present" : "None"}</span>
                </div>
                <SignalBar label="Attribution Score" value={result.analysis.source_analysis.attribution_score} />
              </div>
            </div>

            <div className="col-span-12 md:col-span-6 p-6">
              <div className="label-uppercase mb-3">Fact-Check & Topics</div>
              <div className="mb-4">
                <div className="label-uppercase text-neutral-400 mb-2">Fact-Check Status</div>
                {result.analysis.fact_check_results.claims_checked > 0 ? (
                  <div className="space-y-2">
                    {result.analysis.fact_check_results.matches.map((m, i) => (
                      <div key={i} className="border border-ink p-3">
                        <div className="font-serif font-bold text-sm">{m.verdict}</div>
                        <div className="font-mono text-xs text-neutral-500">{m.publisher}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="font-mono text-xs uppercase tracking-widest text-neutral-500">
                    {result.analysis.fact_check_results.google_fact_check_available ? "No matching claims found" : "Fact-check API unavailable"}
                  </div>
                )}
                {result.analysis.fact_check_results.claimbuster_available && result.analysis.fact_check_results.claimbuster_score !== undefined && (
                  <div className="mt-2 font-mono text-xs text-neutral-400">
                    Checkworthiness score: {(result.analysis.fact_check_results.claimbuster_score * 100).toFixed(0)}%
                  </div>
                )}
              </div>
              <div>
                <div className="label-uppercase text-neutral-400 mb-2">Detected Topics</div>
                {result.analysis.topic_detection.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.analysis.topic_detection.map((t, i) => (
                      <span key={i} className="border border-ink px-2 py-0.5 font-sans text-[10px] uppercase tracking-widest">
                        {t.topic} ({t.relevance.toFixed(0)}%)
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="font-mono text-xs text-neutral-400">No topics detected</span>
                )}
              </div>
            </div>
          </div>

          <div className="border border-ink p-6">
            <div className="label-uppercase mb-3">Analysis Breakdown</div>
            <div className="space-y-2">
              <SignalBar label="Linguistic Signals" value={result.verdict.signal_weights.linguistic * 100} />
              <SignalBar label="Emotional Language" value={result.verdict.signal_weights.emotional * 100} />
              <SignalBar label="Source Reliability" value={result.verdict.signal_weights.source_reliability * 100} />
              <SignalBar label="Fact-Check Risk" value={result.verdict.signal_weights.fact_check_risk * 100} />
              <SignalBar label="Sentiment Extremity" value={result.verdict.signal_weights.sentiment_extremity * 100} />
            </div>
          </div>

          {((result.analysis.entity_extraction.people?.length || 0) +
            (result.analysis.entity_extraction.organizations?.length || 0) +
            (result.analysis.entity_extraction.locations?.length || 0)) > 0 && (
            <div className="border border-ink p-6">
              <div className="label-uppercase mb-3">Entity Extraction</div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="label-uppercase text-neutral-400 mb-2">People</div>
                  {result.analysis.entity_extraction.people.length > 0 ? (
                    result.analysis.entity_extraction.people.map((p, i) => (
                      <span key={i} className="border border-ink px-2 py-0.5 font-mono text-xs mr-1 inline-block mb-1">{p}</span>
                    ))
                  ) : <span className="font-mono text-[10px] text-neutral-400 uppercase tracking-widest">None detected</span>}
                </div>
                <div>
                  <div className="label-uppercase text-neutral-400 mb-2">Organizations</div>
                  {result.analysis.entity_extraction.organizations.length > 0 ? (
                    result.analysis.entity_extraction.organizations.map((o, i) => (
                      <span key={i} className="border border-ink px-2 py-0.5 font-mono text-xs mr-1 inline-block mb-1">{o}</span>
                    ))
                  ) : <span className="font-mono text-[10px] text-neutral-400 uppercase tracking-widest">None detected</span>}
                </div>
                <div>
                  <div className="label-uppercase text-neutral-400 mb-2">Locations</div>
                  {result.analysis.entity_extraction.locations.length > 0 ? (
                    result.analysis.entity_extraction.locations.map((l, i) => (
                      <span key={i} className="border border-ink px-2 py-0.5 font-mono text-xs mr-1 inline-block mb-1">{l}</span>
                    ))
                  ) : <span className="font-mono text-[10px] text-neutral-400 uppercase tracking-widest">None detected</span>}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}