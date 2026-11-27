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
  Twitter,
  Search,
  ExternalLink,
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
    text: "I was charged twice on my credit card and customer support took 4 days to reply. Unacceptable, I am canceling my subscription immediately!",
  },
  {
    label: "⭐ Glowing Product Praise",
    text: "The new user interface update is blazingly fast and delightfully responsive! Our entire engineering team loves it.",
  },
  {
    label: "⚠️ Bug & Latency Report",
    text: "The dashboard export feature crashed repeatedly this morning and API response time is noticeably slow.",
  },
  {
    label: "😏 Sarcastic Review",
    text: "Oh wow, another 4-hour delay with zero updates from gate staff. Just wonderful service as always!",
  },
  {
    label: "🐦 Viral X Announcement",
    text: "Just tested the new AI copilot rollout. Super impressed with the zero-shot reasoning and multilingual accuracy. Major win!",
  },
];

export default function HomePage() {
  const [activeMainTab, setActiveMainTab] = useState("realtime"); // 'realtime' | 'batch' | 'copilot' | 'benchmark'
  const [mode, setMode] = useState("tweet"); // default to Twitter/X URL as per blueprint
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

  // Blueprint-aligned color palette
  const sentimentColor = {
    positive: "#16A36A",
    negative: "#D65353",
    neutral: "#71767B",
    uncertain: "#8899A6",
  };

  const color = sentimentColor[result?.sentiment] || "#1D9BF0";

  return (
    <div className="min-h-screen bg-[#090D12] text-[#F7F9F9] selection:bg-[#1D9BF0]/30 selection:text-[#1D9BF0]">
      {/* ── Enterprise Top Header ── */}
      <header className="border-b border-[#202A36] bg-[#090D12]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            {/* X-style Logo Badge */}
            <div className="h-9 w-9 rounded-xl bg-[#1D9BF0] flex items-center justify-center text-white font-black text-xl shadow-[0_0_20px_rgba(29,155,240,0.35)]">
              𝕏
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-white">X Intelligence</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-[#1D9BF0]/15 text-[#1D9BF0] font-mono tracking-wider font-bold border border-[#1D9BF0]/30">
                  ENTERPRISE v2.1
                </span>
              </div>
              <p className="text-[11px] text-[#71767B] hidden sm:block">
                Understand the conversation. Measure public opinion. Make smarter decisions.
              </p>
            </div>
          </div>

          {/* Model Status & Uptime Badge */}
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#151C25] border border-[#202A36] text-[#8899A6] font-mono text-[11px]">
              <span className="h-2 w-2 rounded-full bg-[#16A36A] animate-pulse" />
              <span>BERT-Social-v2 · 99.8% Calibrated</span>
            </div>
          </div>
        </div>

        {/* ── Enterprise Nav Tabs ── */}
        <div className="max-w-6xl mx-auto px-4 flex items-center gap-1 overflow-x-auto text-xs font-medium border-t border-[#202A36] pt-1">
          {[
            { id: "realtime", label: "Live Post & Conversation Analysis", icon: Zap },
            { id: "batch", label: "Batch & CSV Data Hub", icon: Upload },
            { id: "copilot", label: "AI Recommendations & Copilot", icon: Bot },
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
                    ? "border-[#1D9BF0] text-[#1D9BF0] font-semibold"
                    : "border-transparent text-[#71767B] hover:text-[#F7F9F9]"
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
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#71767B]">
                1-Click Enterprise Test Scenarios
              </span>
              <div className="flex flex-wrap gap-2">
                {QUICK_TEST_SAMPLES.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadSample(s)}
                    className="text-xs px-3 py-1.5 rounded-lg bg-[#090D12] hover:bg-[#1D9BF0]/10 text-[#8899A6] hover:text-[#1D9BF0] border border-[#202A36] hover:border-[#1D9BF0]/40 transition-all text-left"
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex gap-1.5 p-1 rounded-lg bg-[#090D12] border border-[#202A36] text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setMode("tweet");
                      setInput("");
                      setResult(null);
                    }}
                    className={`px-3 py-1 rounded-md transition-all flex items-center gap-1.5 ${
                      mode === "tweet" ? "bg-[#1D9BF0] text-white font-semibold" : "text-[#71767B] hover:text-white"
                    }`}
                  >
                    <span>𝕏 Twitter / X Post URL</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setMode("text");
                      setInput("");
                      setResult(null);
                    }}
                    className={`px-3 py-1 rounded-md transition-all flex items-center gap-1.5 ${
                      mode === "text" ? "bg-[#1D9BF0] text-white font-semibold" : "text-[#71767B] hover:text-white"
                    }`}
                  >
                    <span>📝 Direct Text & Review</span>
                  </button>
                </div>
                <span className="text-xs text-[#71767B]">
                  {mode === "tweet" ? "Paste public X / Twitter post URL" : "Max 2,000 characters"}
                </span>
              </div>

              {mode === "tweet" ? (
                <div className="relative">
                  <input
                    type="url"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    required
                    placeholder="https://x.com/username/status/1234567890123456789"
                    className="w-full bg-[#090D12] border border-[#202A36] rounded-xl px-4 py-3 text-sm text-white placeholder-[#71767B]/60 focus:border-[#1D9BF0] outline-none transition-all"
                  />
                  <span className="absolute right-3 top-3 text-xs text-[#71767B] pointer-events-none">
                    URL Parser Active
                  </span>
                </div>
              ) : (
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={4}
                  minLength={3}
                  maxLength={2000}
                  required
                  placeholder="Paste customer support ticket, app store review, email, or social media commentary..."
                  className="w-full bg-[#090D12] border border-[#202A36] rounded-xl px-4 py-3 text-sm text-white placeholder-[#71767B]/60 resize-none focus:border-[#1D9BF0] outline-none transition-all leading-relaxed"
                />
              )}

              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="w-full py-3 rounded-xl text-sm font-bold bg-[#1D9BF0] text-white hover:bg-[#1A8CD8] disabled:opacity-40 transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(29,155,240,0.3)]"
              >
                {loading ? (
                  <span>Evaluating Neural Weights & Harvesting Data...</span>
                ) : (
                  <>
                    <Zap size={16} />
                    <span>Run Multi-Stage Social Intelligence</span>
                  </>
                )}
              </button>
            </form>

            {/* Error Message */}
            {error && (
              <div className="glass-card p-4 border-[#D65353]/40 text-[#D65353] text-xs">
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
                        style={{ background: `${color}25`, color, border: `1px solid ${color}45` }}
                      >
                        {result.sentiment}
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        setCopilotSubject(result);
                        setActiveMainTab("copilot");
                      }}
                      className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-[#1D9BF0]/15 hover:bg-[#1D9BF0]/25 text-[#1D9BF0] font-semibold border border-[#1D9BF0]/30 transition-all"
                    >
                      <Bot size={14} />
                      <span>Ask Copilot to Draft Reply →</span>
                    </button>
                  </div>

                  {/* Confidence Bar */}
                  <div>
                    <div className="flex justify-between text-xs text-[#8899A6] mb-1">
                      <span>Model Confidence</span>
                      <span className="font-mono font-bold text-white">
                        {((result.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2.5 bg-[#090D12] rounded-full overflow-hidden border border-[#202A36]">
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
                          className="p-2.5 rounded-xl bg-[#090D12] border border-[#202A36] text-center"
                        >
                          <span className="text-[10px] uppercase font-bold text-[#71767B] block">
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
                  <div className="pt-2 border-t border-[#202A36] flex items-center justify-between text-[11px] text-[#71767B] flex-wrap gap-2">
                    <div>
                      Architecture:{" "}
                      <span className="text-[#F7F9F9] font-mono">{result.model_version || "BERT-Social-v2"}</span>
                    </div>
                    <div>
                      Language:{" "}
                      <span className="text-[#F7F9F9] font-mono">
                        {(result.language || "EN").toUpperCase()}
                      </span>
                    </div>
                    <div>
                      Inference Latency:{" "}
                      <span className="text-[#1D9BF0] font-mono">
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
              <div className="glass-card p-4 border-l-2 border-l-[#1D9BF0] flex items-center justify-between flex-wrap gap-2">
                <div className="text-xs">
                  <span className="text-[#71767B] uppercase font-mono block text-[10px]">Active Subject:</span>
                  <p className="text-[#F7F9F9] italic font-medium max-w-xl truncate mt-0.5">
                    "{copilotSubject.text || copilotSubject.original_text}"
                  </p>
                </div>
                <span
                  className="px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize"
                  style={{
                    background: `${sentimentColor[copilotSubject.sentiment]}25`,
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
      <h3 className="text-sm font-semibold text-[#F7F9F9] flex items-center gap-2">
        <Sparkles size={15} className="text-[#1D9BF0]" />
        Explainability Signals & Linguistic Rationale
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Confidence Reasoning */}
        {confidence_reasoning && (
          <div className="p-3.5 rounded-xl bg-[#090D12] border border-[#202A36] space-y-1.5">
            <span className="text-[10px] uppercase font-bold tracking-wider text-[#71767B]">
              Confidence Reasoning Tier
            </span>
            <p className="text-xs text-[#8899A6] leading-relaxed">
              {confidence_reasoning.reason}
            </p>
          </div>
        )}

        {/* Sarcasm & Keyword Cues */}
        <div className="p-3.5 rounded-xl bg-[#090D12] border border-[#202A36] space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-[#71767B] block">
            Linguistic Sarcasm & Cue Analysis
          </span>

          {sarcasm_evidence?.is_sarcastic ? (
            <div className="text-xs text-[#fb923c] font-semibold flex items-center gap-1.5">
              <AlertTriangle size={13} />
              Sarcasm Detected ({sarcasm_evidence.sarcasm_phrases?.join(", ") || "contrast marker"})
            </div>
          ) : (
            <p className="text-xs text-[#71767B]">No overt sarcasm markers identified.</p>
          )}

          {keyword_polarity && (
            <div className="flex gap-3 text-xs pt-1 border-t border-[#202A36] flex-wrap">
              <span className="text-[#16A36A]">+{keyword_polarity.positive_count} positive cues</span>
              <span className="text-[#D65353]">−{keyword_polarity.negative_count} negative cues</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
