"use client";
import { useState } from "react";
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  MessageSquareQuote,
  Minus,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react";

/**
 * EvidencePanel — Phase 5 / Phase 6
 *
 * Renders the structured evidence bundle returned by /api/v1/predict/explain:
 *   • Confidence reasoning tier + rationale
 *   • Keyword polarity breakdown (positive / negative / negated)
 *   • Sarcasm evidence signals
 *
 * Fully keyboard-navigable, ARIA-labeled, and screen-reader friendly.
 */
export default function EvidencePanel({ evidence }) {
  const [open, setOpen] = useState(false);

  if (!evidence) return null;

  const { sarcasm_evidence, keyword_polarity, confidence_reasoning } = evidence;

  const tierColors = {
    high: "#00F5A0",
    moderate: "#facc15",
    low: "#fb923c",
    abstained: "#f87171",
  };
  const tier = confidence_reasoning?.confidence_tier ?? "moderate";
  const tierColor = tierColors[tier] ?? "#60a5fa";

  return (
    <section
      aria-label="Prediction evidence and explainability"
      className="glass-card p-4 space-y-3"
    >
      {/* ── Collapsible header ── */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="evidence-panel-body"
        className="w-full flex items-center justify-between gap-3 text-left group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00F5A0] rounded-md"
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-white/80 group-hover:text-white transition-colors">
          <Zap size={15} className="text-[#00F5A0]" aria-hidden="true" />
          Prediction Evidence
        </span>
        <span className="text-white/40" aria-hidden="true">
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </span>
      </button>

      {/* ── Expandable body ── */}
      <div
        id="evidence-panel-body"
        hidden={!open}
        className={open ? "space-y-4" : ""}
      >
        {/* Confidence Reasoning */}
        {confidence_reasoning && (
          <div
            role="region"
            aria-label="Confidence reasoning"
            className="rounded-lg border border-white/8 bg-black/20 p-3 space-y-1"
          >
            <p className="text-[10px] uppercase tracking-wider text-white/35 font-medium">
              Confidence Reasoning
            </p>
            <span
              className="inline-block px-2 py-0.5 rounded-full text-[11px] font-semibold capitalize"
              style={{ background: `${tierColor}20`, color: tierColor, border: `1px solid ${tierColor}40` }}
              aria-label={`Confidence tier: ${tier}`}
            >
              {tier}
            </span>
            <p className="text-xs text-white/60 leading-relaxed mt-1">
              {confidence_reasoning.reason}
            </p>
            <dl className="flex gap-4 mt-2 text-xs text-white/50">
              <div>
                <dt className="inline">Top: </dt>
                <dd className="inline text-white/80 font-mono">
                  {confidence_reasoning.top_class} ({((confidence_reasoning.top_probability ?? 0) * 100).toFixed(1)}%)
                </dd>
              </div>
              <div>
                <dt className="inline">Gap: </dt>
                <dd className="inline text-white/80 font-mono">
                  {((confidence_reasoning.probability_gap ?? 0) * 100).toFixed(1)}%
                </dd>
              </div>
            </dl>
          </div>
        )}

        {/* Keyword Polarity */}
        {keyword_polarity && (
          <div
            role="region"
            aria-label="Keyword polarity breakdown"
            className="rounded-lg border border-white/8 bg-black/20 p-3 space-y-2"
          >
            <p className="text-[10px] uppercase tracking-wider text-white/35 font-medium">
              Keyword Polarity
            </p>
            <div className="flex flex-wrap gap-3 text-xs">
              <span className="flex items-center gap-1 text-[#00F5A0]" aria-label={`${keyword_polarity.positive_count} positive keywords`}>
                <TrendingUp size={12} aria-hidden="true" />
                {keyword_polarity.positive_count} positive
              </span>
              <span className="flex items-center gap-1 text-[#f87171]" aria-label={`${keyword_polarity.negative_count} negative keywords`}>
                <TrendingDown size={12} aria-hidden="true" />
                {keyword_polarity.negative_count} negative
              </span>
              <span className="flex items-center gap-1 text-white/40" aria-label={`${keyword_polarity.negated_count} negated positives`}>
                <Minus size={12} aria-hidden="true" />
                {keyword_polarity.negated_count} negated
              </span>
            </div>

            {/* Positive keyword pills */}
            {keyword_polarity.positive_keywords?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1" aria-label="Positive keywords">
                {keyword_polarity.positive_keywords.slice(0, 8).map((kw) => (
                  <span
                    key={kw}
                    className="px-2 py-0.5 rounded-full text-[10px] bg-[#00F5A0]/10 border border-[#00F5A0]/20 text-[#00F5A0]"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            )}

            {/* Negative keyword pills */}
            {keyword_polarity.negative_keywords?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1" aria-label="Negative keywords">
                {keyword_polarity.negative_keywords.slice(0, 8).map((kw) => (
                  <span
                    key={kw}
                    className="px-2 py-0.5 rounded-full text-[10px] bg-[#f87171]/10 border border-[#f87171]/20 text-[#f87171]"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Sarcasm Evidence */}
        {sarcasm_evidence && (
          <div
            role="region"
            aria-label="Sarcasm evidence signals"
            className="rounded-lg border border-white/8 bg-black/20 p-3 space-y-2"
          >
            <p className="text-[10px] uppercase tracking-wider text-white/35 font-medium">
              Sarcasm Signals
            </p>
            <div className="flex items-center gap-2">
              {sarcasm_evidence.is_sarcastic ? (
                <span
                  className="flex items-center gap-1 text-xs text-[#fb923c] font-medium"
                  role="status"
                  aria-live="polite"
                >
                  <AlertTriangle size={12} aria-hidden="true" />
                  Sarcasm detected
                </span>
              ) : (
                <span className="text-xs text-white/40">No sarcasm detected</span>
              )}
              <span className="text-[10px] text-white/30">
                · {sarcasm_evidence.exclamation_count} exclamation(s)
                {sarcasm_evidence.uppercase_stress ? " · uppercase stress" : ""}
              </span>
            </div>

            {sarcasm_evidence.sarcasm_phrases?.length > 0 && (
              <div className="flex flex-wrap gap-1" aria-label="Detected sarcasm phrases">
                {sarcasm_evidence.sarcasm_phrases.map((p) => (
                  <span
                    key={p}
                    className="px-2 py-0.5 rounded-full text-[10px] bg-[#fb923c]/10 border border-[#fb923c]/20 text-[#fb923c]"
                  >
                    "{p}"
                  </span>
                ))}
              </div>
            )}

            {sarcasm_evidence.contrast_markers?.length > 0 && (
              <p className="text-[10px] text-white/40">
                Contrast markers: {sarcasm_evidence.contrast_markers.join(", ")}
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
