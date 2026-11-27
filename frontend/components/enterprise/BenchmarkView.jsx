"use client";
import { useState } from "react";
import { Scale, Trophy, ArrowRight, Zap, TrendingUp, TrendingDown } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const PRESET_BENCHMARKS = [
  {
    name: "Version 2.0 vs Legacy v1.0",
    labelA: "Platform v2.0 (New)",
    textA: "The latest update is blazingly fast, responsive, and the new dark mode is gorgeous!",
    labelB: "Legacy v1.0 (Old)",
    textB: "The application keeps freezing on exports and the interface looks dated and sluggish.",
  },
  {
    name: "Customer Support vs Shipping",
    labelA: "Support Agent Experience",
    textA: "The customer support representative went above and beyond to solve my problem with genuine empathy.",
    labelB: "Delivery Logistics",
    textB: "Package arrived 5 days late with crushed box and courier was completely unresponsive.",
  },
  {
    name: "Brand A vs Brand B",
    labelA: "CloudSync Pro",
    textA: "Seamless background sync, never experienced a conflict, and billing is totally transparent.",
    labelB: "Competitor Drive",
    textB: "Hidden fees on renewal, overcharged twice, and lost my unsynced documents during crash.",
  },
];

export default function BenchmarkView() {
  const [labelA, setLabelA] = useState(PRESET_BENCHMARKS[0].labelA);
  const [textA, setTextA] = useState(PRESET_BENCHMARKS[0].textA);
  const [labelB, setLabelB] = useState(PRESET_BENCHMARKS[0].labelB);
  const [textB, setTextB] = useState(PRESET_BENCHMARKS[0].textB);

  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState(null);
  const [error, setError] = useState(null);

  const handleRunBenchmark = async (tA, tB, lA, lB) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/v1/enterprise/benchmark`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text_a: tA || textA,
          text_b: tB || textB,
          label_a: lA || labelA,
          label_b: lB || labelB,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Benchmark comparison failed");
      setComparison(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (p) => {
    setLabelA(p.labelA);
    setTextA(p.textA);
    setLabelB(p.labelB);
    setTextB(p.textB);
    handleRunBenchmark(p.textA, p.textB, p.labelA, p.labelB);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-5 space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Scale size={20} className="text-[#1D9BF0]" />
            <h2 className="text-base font-bold text-white">A/B Benchmark & Competitive Compare</h2>
          </div>
          <span className="text-xs text-[#71767B]">Side-by-side Sentiment Delta Analysis</span>
        </div>

        {/* Preset quick buttons */}
        <div className="flex items-center gap-2 flex-wrap pt-1">
          <span className="text-xs text-[#71767B]">Load Preset:</span>
          {PRESET_BENCHMARKS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => loadPreset(p)}
              className="text-xs px-2.5 py-1 rounded-lg bg-[#090D12] hover:bg-[#151C25] text-[#8899A6] hover:text-[#1D9BF0] border border-[#202A36] transition-all"
            >
              ⚖️ {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Input Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Column A */}
        <div className="glass-card p-4 space-y-3 border-l-2 border-l-[#1D9BF0]">
          <div className="flex items-center justify-between">
            <input
              type="text"
              value={labelA}
              onChange={(e) => setLabelA(e.target.value)}
              className="bg-transparent font-bold text-sm text-[#1D9BF0] outline-none border-b border-transparent focus:border-[#1D9BF0]"
            />
            <span className="text-[10px] text-[#71767B] uppercase font-mono">Variant A</span>
          </div>
          <textarea
            value={textA}
            onChange={(e) => setTextA(e.target.value)}
            rows={4}
            className="w-full bg-[#090D12] border border-[#202A36] rounded-lg p-3 text-xs text-white placeholder-[#71767B]/60 outline-none focus:border-[#1D9BF0] resize-none"
            placeholder="Feedback, review, or campaign post for Variant A..."
          />
        </div>

        {/* Column B */}
        <div className="glass-card p-4 space-y-3 border-l-2 border-l-[#8899A6]">
          <div className="flex items-center justify-between">
            <input
              type="text"
              value={labelB}
              onChange={(e) => setLabelB(e.target.value)}
              className="bg-transparent font-bold text-sm text-[#8899A6] outline-none border-b border-transparent focus:border-[#8899A6]"
            />
            <span className="text-[10px] text-[#71767B] uppercase font-mono">Variant B</span>
          </div>
          <textarea
            value={textB}
            onChange={(e) => setTextB(e.target.value)}
            rows={4}
            className="w-full bg-[#090D12] border border-[#202A36] rounded-lg p-3 text-xs text-white placeholder-[#71767B]/60 outline-none focus:border-[#8899A6] resize-none"
            placeholder="Feedback, review, or campaign post for Variant B..."
          />
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={() => handleRunBenchmark()}
          disabled={loading || !textA.trim() || !textB.trim()}
          className="px-6 py-2.5 rounded-xl bg-[#1D9BF0] text-white font-semibold text-sm hover:bg-[#1A8CD8] disabled:opacity-40 transition-all shadow-[0_0_15px_rgba(29,155,240,0.3)]"
        >
          {loading ? "Computing Differential..." : "Run Side-by-Side Benchmark"}
        </button>
      </div>

      {error && (
        <div className="glass-card p-4 border-[#D65353]/40 text-[#D65353] text-xs">
          ⚠️ {error}
        </div>
      )}

      {/* Benchmark Results */}
      {comparison && (
        <div className="glass-card p-6 space-y-5 animate-in fade-in duration-300">
          {/* Winner Banner */}
          <div className="p-4 rounded-xl bg-[#090D12] border border-[#1D9BF0]/40 flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-[#1D9BF0]/20 text-[#1D9BF0]">
                <Trophy size={22} />
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-[#71767B]">
                  Competitive Verdict
                </span>
                <h3 className="text-base font-bold text-white">
                  Leader: <span className="text-[#1D9BF0]">{comparison.winner}</span>
                </h3>
              </div>
            </div>
            <p className="text-xs text-[#8899A6] max-w-md">{comparison.verdict}</p>
          </div>

          {/* Cards comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[comparison.option_a, comparison.option_b].map((opt, i) => (
              <div
                key={i}
                className={`p-4 rounded-xl border bg-[#090D12] space-y-3 ${
                  opt.label === comparison.winner ? "border-[#1D9BF0]/50" : "border-[#202A36]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-white">{opt.label}</h4>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize ${
                      opt.sentiment === "positive"
                        ? "bg-[#16A36A]/15 text-[#16A36A]"
                        : opt.sentiment === "negative"
                        ? "bg-[#D65353]/15 text-[#D65353]"
                        : "bg-[#71767B]/15 text-[#71767B]"
                    }`}
                  >
                    {opt.sentiment} ({(opt.confidence * 100).toFixed(1)}%)
                  </span>
                </div>

                <p className="text-xs text-[#8899A6] italic border-l-2 border-[#202A36] pl-2.5">
                  "{opt.text}"
                </p>

                {opt.triage && (
                  <div className="text-[11px] text-[#71767B] space-y-1 pt-1 border-t border-[#202A36]">
                    <div>
                      <span className="text-[#71767B]">Urgency:</span> {opt.triage.urgency} ·{" "}
                      <span className="text-[#71767B]">Intent:</span> {opt.triage.intent}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
