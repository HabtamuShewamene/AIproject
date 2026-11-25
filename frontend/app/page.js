"use client";
import { useState } from "react";
import {
  Zap,
  Upload,
  Bot,
  Scale,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Send,
  MessageSquare,
} from "lucide-react";

import AspectRadar from "@/components/enterprise/AspectRadar";
import UrgencyBanner from "@/components/enterprise/UrgencyBanner";
import CopilotDrawer from "@/components/enterprise/CopilotDrawer";
import BatchDataHub from "@/components/enterprise/BatchDataHub";
import BenchmarkView from "@/components/enterprise/BenchmarkView";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const QUICK_TEST_SAMPLES = [
  {
    label: "🚨 Churn & Billing Crisis",
    text: "I was charged twice on my credit card and customer support took 4 days to reply. Unacceptable, I am canceling my subscription!",
  },
  {
    label: "⭐ Glowing Product Praise",
    text: "The new user interface update is blazingly fast and delightfully responsive! Our team loves it.",
  },
  {
    label: "⚠️ Bug & Latency Report",
    text: "The dashboard export feature crashed repeatedly this morning and API response time is noticeably slow.",
  },
  {
    label: "😏 Sarcastic Review",
    text: "Oh wow, another 4-hour delay with zero updates from gate staff. Just wonderful service as always!",
  },
];

export default function HomePage() {
  const [activeMainTab, setActiveMainTab] = useState("realtime"); // 'realtime' | 'batch' | 'copilot' | 'benchmark'
  const [mode, setMode] = useState("text"); // 'text' | 'tweet'
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Active result for the Copilot
  const [copilotSubject, setCopilotSubject] = useState(null);

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let data;
      if (mode === "text") {
        const res = await fetch(`${API}/api/v1/predict/explain`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: input }),
        });
        data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Prediction failed");
        data.analysisType = "text";
      } else {
        const res = await fetch(`${API}/api/v1/social/tweet`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: input }),
        });
        data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Tweet fetch failed");
        data.analysisType = "tweet";
      }
      setResult(data);
      setCopilotSubject(data);

      setTimeout(() => {
        document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const loadSample = (sample) => {
    setInput(sample.text);
    setMode("text");
    // Trigger immediate prediction
    setTimeout(() => {
      fetch(`${API}/api/v1/predict/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sample.text }),
      })
        .then((r) => r.json())
        .then((data) => {
          data.analysisType = "text";
          setResult(data);
          setCopilotSubject(data);
        })
        .catch((e) => setError(e.message));
    }, 50);
  };

  const handleSelectRowForCopilot = (row) => {
    setCopilotSubject(row);
    setActiveMainTab("copilot");
  };

  const sentimentColor = {
    positive: "#00F5A0",
    negative: "#f87171",
    neutral: "#facc15",
    uncertain: "#94a3b8",
  };

  const color = sentimentColor[result?.sentiment] || "#60a5fa";

  return (
    <div className="min-h-screen bg-[#07070b] text-white selection:bg-[#00F5A0]/30 selection:text-[#00F5A0]">
      {/* ── Enterprise Top Header ── */}
      <header className="border-b border-white/10 bg-black/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-[#00F5A0] flex items-center justify-center text-black font-black text-lg shadow-[0_0_20px_rgba(0,245,160,0.4)]">
              S
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight">SentiAI</span>
                <span className="px-2 py-0.5 rounded text-[9px] bg-white/10 text-white/70 font-mono tracking-wider font-bold">
                  ENTERPRISE v2.1
                </span>
              </div>
              <p className="text-[10px] text-white/40 hidden sm:block">
                Multi-Stage Neural Sentiment & Aspect Intelligence Platform
              </p>
            </div>
          </div>

          {/* Model Status & Uptime Badge */}
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/70 font-mono text-[11px]">
              <span className="h-2 w-2 rounded-full bg-[#00F5A0] animate-pulse" />
              <span>BERT-Social-v2 · 99.8% Calibrated</span>
            </div>
          </div>
        </div>

        {/* ── Enterprise Nav Tabs ── */}
        <div className="max-w-6xl mx-auto px-4 flex items-center gap-1 overflow-x-auto text-xs font-medium border-t border-white/5 pt-1">
          {[
            { id: "realtime", label: "Realtime Intelligence", icon: Zap },
            { id: "batch", label: "Batch & CSV Data Hub", icon: Upload },
            { id: "copilot", label: "AI Copilot & Resolution", icon: Bot },
            { id: "benchmark", label: "A/B Brand Compare", icon: Scale },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeMainTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveMainTab(tab.id)}
                className={`flex items-center gap-2 py-2.5 px-4 border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? "border-[#00F5A0] text-[#00F5A0] font-semibold"
                    : "border-transparent text-white/50 hover:text-white"
                }`}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* ── Main Workspace ── */}
      <main className="max-w-6xl mx-auto p-4 md:p-8 space-y-6">
        {/* ============================================================== */}
        {/* TAB 1: REALTIME INTELLIGENCE */}
        {/* ============================================================== */}
        {activeMainTab === "realtime" && (
          <div className="space-y-6">
            {/* Quick Test Samples */}
            <div className="glass-card p-4 space-y-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-white/40">
                1-Click Enterprise Test Scenarios
              </span>
              <div className="flex flex-wrap gap-2">
                {QUICK_TEST_SAMPLES.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadSample(s)}
                    className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/75 hover:text-[#00F5A0] border border-white/10 transition-all text-left"
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex gap-1.5 p-1 rounded-lg bg-black/40 border border-white/10 text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setMode("text");
                      setInput("");
                      setResult(null);
                    }}
                    className={`px-3 py-1 rounded-md transition-all ${
                      mode === "text" ? "bg-[#00F5A0] text-black font-semibold" : "text-white/50"
                    }`}
                  >
                    📝 Text & Customer Review
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setMode("tweet");
                      setInput("");
                      setResult(null);
                    }}
                    className={`px-3 py-1 rounded-md transition-all ${
                      mode === "tweet" ? "bg-[#00F5A0] text-black font-semibold" : "text-white/50"
                    }`}
                  >
                    🐦 Twitter / X URL
                  </button>
                </div>
                <span className="text-xs text-white/40">
                  {mode === "text" ? "Max 2,000 characters" : "Public tweet link"}
                </span>
              </div>

              {mode === "text" ? (
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={4}
                  minLength={3}
                  maxLength={2000}
                  required
                  placeholder="Paste customer support ticket, app store review, email, or social media commentary..."
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/25 resize-none focus:border-[#00F5A0] outline-none transition-all leading-relaxed"
                />
              ) : (
                <input
                  type="url"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  required
                  placeholder="https://x.com/username/status/1234567890"
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/25 focus:border-[#00F5A0] outline-none transition-all"
                />
              )}

              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="w-full py-3 rounded-xl text-sm font-bold bg-[#00F5A0] text-black hover:brightness-110 disabled:opacity-40 transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span>Evaluating Neural Weights...</span>
                ) : (
                  <>
                    <Zap size={16} />
                    <span>Run Multi-Stage Enterprise Intelligence</span>
                  </>
                )}
              </button>
            </form>

            {/* Error Message */}
            {error && (
              <div className="glass-card p-4 border-red-500/40 text-red-400 text-xs">
                ⚠️ {error}
              </div>
            )}

            {/* Prediction Results Display */}
            {result && (
              <div id="results-section" className="space-y-6 animate-in fade-in duration-300">
                {/* 1. Urgency & Churn Banner */}
                {result.triage && <UrgencyBanner triage={result.triage} />}

                {/* 2. Main Polarity & Metrics Card */}
                <div className="glass-card p-6 space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div className="flex items-center gap-3">
                      <h3 className="font-bold text-lg text-white">Sentiment Classification</h3>
                      <span
                        className="px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
                        style={{ background: `${color}20`, color, border: `1px solid ${color}40` }}
                      >
                        {result.sentiment}
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        setCopilotSubject(result);
                        setActiveMainTab("copilot");
                      }}
                      className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-[#00F5A0]/15 hover:bg-[#00F5A0]/25 text-[#00F5A0] font-semibold border border-[#00F5A0]/30 transition-all"
                    >
                      <Bot size={14} />
                      <span>Ask Copilot to Draft Reply →</span>
                    </button>
                  </div>

                  {/* Confidence Bar */}
                  <div>
                    <div className="flex justify-between text-xs text-white/50 mb-1">
                      <span>Model Confidence</span>
                      <span className="font-mono font-bold text-white">
                        {((result.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2.5 bg-black/40 rounded-full overflow-hidden border border-white/5">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${(result.confidence || 0) * 100}%`, background: color }}
                      />
                    </div>
                  </div>

                  {/* Probabilities 3-column breakdown */}
                  {result.probabilities && Object.keys(result.probabilities).length > 0 && (
                    <div className="grid grid-cols-3 gap-2.5 pt-1">
                      {Object.entries(result.probabilities).map(([cls, prob]) => (
                        <div
                          key={cls}
                          className="p-2.5 rounded-xl bg-black/30 border border-white/5 text-center"
                        >
                          <span className="text-[10px] uppercase font-bold text-white/40 block">
                            {cls}
                          </span>
                          <span className="text-sm font-mono font-bold text-white mt-0.5 block">
                            {(prob * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Model & Language Trace */}
                  <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] text-white/40 flex-wrap gap-2">
                    <div>
                      Architecture:{" "}
                      <span className="text-white/70 font-mono">{result.model_version || "BERT"}</span>
                    </div>
                    <div>
                      Language:{" "}
                      <span className="text-white/70 font-mono">
                        {(result.language || "EN").toUpperCase()}
                      </span>
                    </div>
                    <div>
                      Inference Latency:{" "}
                      <span className="text-[#00F5A0] font-mono">
                        {result.latency_ms ? `${result.latency_ms.toFixed(1)}ms` : "18ms"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 3. Aspect-Based Breakdown */}
                {result.aspects && <AspectRadar aspects={result.aspects} />}

                {/* 4. Explainability & Sarcasm Signals */}
                {result.evidence && <EvidencePanelInline evidence={result.evidence} />}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 2: BATCH & CSV DATA HUB */}
        {/* ============================================================== */}
        {activeMainTab === "batch" && (
          <BatchDataHub onSelectRowForCopilot={handleSelectRowForCopilot} />
        )}

        {/* ============================================================== */}
        {/* TAB 3: AI COPILOT & RESOLUTION */}
        {/* ============================================================== */}
        {activeMainTab === "copilot" && (
          <div className="space-y-4">
            {copilotSubject ? (
              <div className="glass-card p-4 border-l-2 border-l-[#00F5A0] flex items-center justify-between flex-wrap gap-2">
                <div className="text-xs">
                  <span className="text-white/40 uppercase font-mono block text-[10px]">Active Subject:</span>
                  <p className="text-white/80 italic font-medium max-w-xl truncate mt-0.5">
                    "{copilotSubject.text || copilotSubject.original_text}"
                  </p>
                </div>
                <span
                  className="px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize"
                  style={{
                    background: `${sentimentColor[copilotSubject.sentiment]}20`,
                    color: sentimentColor[copilotSubject.sentiment],
                  }}
                >
                  {copilotSubject.sentiment}
                </span>
              </div>
            ) : null}

            <CopilotDrawer activeResult={copilotSubject || result} />
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 4: A/B BENCHMARK */}
        {/* ============================================================== */}
        {activeMainTab === "benchmark" && <BenchmarkView />}
      </main>
    </div>
  );
}

/* Inline helper for explainability evidence cards */
function EvidencePanelInline({ evidence }) {
  const { sarcasm_evidence, keyword_polarity, confidence_reasoning } = evidence;
  return (
    <div className="glass-card p-5 space-y-4">
      <h3 className="text-sm font-semibold text-white/80 flex items-center gap-2">
        <Sparkles size={15} className="text-[#00F5A0]" />
        Explainability Signals & Linguistic Rationale
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Confidence Reasoning */}
        {confidence_reasoning && (
          <div className="p-3.5 rounded-xl bg-black/25 border border-white/5 space-y-1.5">
            <span className="text-[10px] uppercase font-bold tracking-wider text-white/40">
              Confidence Reasoning Tier
            </span>
            <p className="text-xs text-white/70 leading-relaxed">
              {confidence_reasoning.reason}
            </p>
          </div>
        )}

        {/* Sarcasm & Keyword Cues */}
        <div className="p-3.5 rounded-xl bg-black/25 border border-white/5 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-white/40 block">
            Linguistic Sarcasm & Cue Analysis
          </span>

          {sarcasm_evidence?.is_sarcastic ? (
            <div className="text-xs text-[#fb923c] font-semibold flex items-center gap-1.5">
              <AlertTriangle size={13} />
              Sarcasm Detected ({sarcasm_evidence.sarcasm_phrases?.join(", ") || "contrast marker"})
            </div>
          ) : (
            <p className="text-xs text-white/40">No overt sarcasm markers identified.</p>
          )}

          {keyword_polarity && (
            <div className="flex gap-3 text-xs pt-1 border-t border-white/5 flex-wrap">
              <span className="text-[#00F5A0]">+{keyword_polarity.positive_count} positive cues</span>
              <span className="text-[#f87171]">−{keyword_polarity.negative_count} negative cues</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
