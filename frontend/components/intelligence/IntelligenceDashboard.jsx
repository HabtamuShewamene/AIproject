"use client";

import Badge from "@/components/ui/Badge";
import { toConfidencePercent } from "@/utils/analytics";
import {
  Activity,
  ArrowUpRight,
  Bot,
  FileText,
  Globe2,
  MessageCircle,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";

function formatText(value, fallback = "—") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  return String(value);
}

function formatCount(value) {
  const number = Number(value ?? 0);
  return Number.isFinite(number) ? number.toLocaleString("en-US") : "0";
}

function InsightCard({ icon: Icon, label, value, helper, tone = "neutral" }) {
  const toneClasses =
    tone === "positive"
      ? "border-emerald-500/20 bg-emerald-500/5 text-emerald-300"
      : tone === "negative"
        ? "border-red-500/20 bg-red-500/5 text-red-300"
        : tone === "warning"
          ? "border-amber-500/20 bg-amber-500/5 text-amber-300"
          : "border-white/10 bg-white/[0.03] text-white";

  return (
    <div className={`rounded-2xl border p-3 ${toneClasses}`}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
          <Icon size={13} />
          {label}
        </div>
        <span className="text-sm font-semibold text-white">{value}</span>
      </div>
      {helper ? <p className="mt-2 text-xs leading-relaxed text-white/45">{helper}</p> : null}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      <div className="h-28 rounded-2xl border border-white/10 bg-white/[0.03] animate-pulse" />
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="h-20 rounded-2xl border border-white/10 bg-white/[0.03] animate-pulse" />
        <div className="h-20 rounded-2xl border border-white/10 bg-white/[0.03] animate-pulse" />
      </div>
      <div className="h-20 rounded-2xl border border-white/10 bg-white/[0.03] animate-pulse" />
    </div>
  );
}

export default function IntelligenceDashboard({ result, loading = false }) {
  const analysisType = (result?.analysisType || "text").toLowerCase();
  const sentiment = (result?.sentiment || "neutral").toLowerCase();
  const confidencePercent = toConfidencePercent(result?.confidence);
  const language = formatText(result?.language, "Unknown");
  const sourceLabel =
    analysisType === "topic" ? "Topic sweep" : analysisType === "url" ? "Tweet capture" : "Custom text";
  const sourceDetail =
    analysisType === "topic"
      ? formatText(result?.topic || result?.query, "No topic provided")
      : analysisType === "url"
        ? formatText(result?.original_text || result?.tweet_text, "No tweet text available")
        : formatText(result?.original_text, "No text available");
  const summary = analysisType === "topic" ? result?.summary || {} : null;
  const metrics = result?.metrics || null;
  const translatedText = formatText(result?.translated_text, "");
  const originalText = formatText(result?.original_text, "");
  const hasTranslation = translatedText && translatedText !== originalText;
  const totalPosts = Number(summary?.total ?? result?.total_tweets ?? 0);

  return (
    <div className="grid gap-3 xl:grid-cols-[1.05fr_0.95fr]">
      <section className="glass-card p-5 space-y-4 min-h-[260px]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
              <Activity size={13} />
              Intelligence layer
            </div>
            <h3 className="text-base font-semibold text-white">Live sentiment interpretation</h3>
            <p className="max-w-2xl text-sm leading-relaxed text-white/45">
              The dashboard combines the current analysis output with language, confidence, and source context so you can
              understand why the model reached its decision.
            </p>
          </div>
          <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
            <div
              className="flex h-16 w-16 items-center justify-center rounded-full border border-[#00F5A0]/20 bg-[#00F5A0]/10 text-center text-sm font-bold text-[#00F5A0]"
              style={{
                backgroundImage: `conic-gradient(#00F5A0 ${confidencePercent}%, rgba(255,255,255,0.08) ${confidencePercent}% 100%)`,
              }}
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-full bg-[#07121a] text-[11px] text-white/80">
                {confidencePercent}%
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
                <ShieldCheck size={13} />
                Confidence
              </div>
              <p className="mt-1 text-sm text-white/75">
                Current sentiment: <span className="font-semibold text-white">{sentiment}</span>
              </p>
              <div className="mt-2">
                <Badge sentiment={sentiment} />
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton />
        ) : (
          <>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <InsightCard
                icon={Bot}
                label="Analysis mode"
                value={analysisType}
                helper="Current output format returned by the backend."
              />
              <InsightCard
                icon={Globe2}
                label="Language"
                value={language}
                helper="Detected or returned language context."
              />
              <InsightCard
                icon={Sparkles}
                label="Confidence"
                value={`${confidencePercent}%`}
                helper="Model certainty after normalisation."
                tone={sentiment === "positive" ? "positive" : sentiment === "negative" ? "negative" : "warning"}
              />
              <InsightCard
                icon={ScanSearch}
                label="Source"
                value={sourceLabel}
                helper={analysisType === "topic" ? "Topic-based summary from recent posts." : "Single-item analysis."}
              />
            </div>

            <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
                  <FileText size={13} />
                  Source context
                </div>
                <p className="mt-3 text-sm leading-relaxed text-white/70">
                  {sourceDetail}
                </p>
                {hasTranslation ? (
                  <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-3">
                    <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-white/35">
                      <ArrowUpRight size={12} />
                      Translated text
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-white/65">{translatedText}</p>
                  </div>
                ) : null}
              </div>

              <div className="space-y-3">
                {analysisType === "topic" ? (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
                      <Users size={13} />
                      Topic summary
                    </div>
                    {totalPosts > 0 ? (
                      <div className="mt-3 space-y-3">
                        <InsightCard icon={MessageCircle} label="Total posts" value={formatCount(totalPosts)} helper="Combined topic sample size." />
                        <InsightCard icon={Sparkles} label="Positive" value={formatCount(summary?.positive)} tone="positive" helper="Positive share in the topic sample." />
                        <InsightCard icon={Bot} label="Negative" value={formatCount(summary?.negative)} tone="negative" helper="Negative share in the topic sample." />
                        <InsightCard icon={Activity} label="Neutral" value={formatCount(summary?.neutral)} tone="warning" helper="Neutral share in the topic sample." />
                      </div>
                    ) : (
                      <div className="mt-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
                        No posts were returned for this topic yet. Try a broader query or check the scraper setup.
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
                      <MessageCircle size={13} />
                      Payload summary
                    </div>
                    <div className="mt-3 space-y-3">
                      <InsightCard
                        icon={FileText}
                        label="Original text"
                        value={originalText ? "Available" : "Missing"}
                        helper={originalText || "No original text returned."}
                        tone={originalText ? "positive" : "warning"}
                      />
                      <InsightCard
                        icon={Globe2}
                        label="Translation"
                        value={hasTranslation ? "Available" : "Not needed"}
                        helper={hasTranslation ? translatedText : "No translated text returned."}
                      />
                      {metrics ? (
                        <div className="grid grid-cols-2 gap-3 pt-1">
                          <InsightCard icon={Sparkles} label="Likes" value={formatCount(metrics.likes)} helper="Engagement on the source post." />
                          <InsightCard icon={ArrowUpRight} label="Retweets" value={formatCount(metrics.retweets)} helper="Amplification count." />
                          <InsightCard icon={Users} label="Replies" value={formatCount(metrics.replies)} helper="Conversation depth." />
                          <InsightCard icon={Activity} label="Quotes" value={formatCount(metrics.views)} helper="Quoted reposts returned by the API." />
                        </div>
                      ) : null}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </section>

      <section className="glass-card p-5 space-y-4 min-h-[260px]">
        <div>
          <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white/40">
            <Sparkles size={13} />
            Intelligence notes
          </div>
          <h3 className="mt-2 text-base font-semibold text-white">What the dashboard is surfacing</h3>
        </div>

        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="space-y-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/35">Dominant signal</p>
              <p className="mt-2 text-sm leading-relaxed text-white/70">
                The analysis currently leans <span className="font-semibold text-white">{sentiment}</span> with a
                confidence score of <span className="font-semibold text-white">{confidencePercent}%</span>.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <InsightCard
                icon={ShieldCheck}
                label="Trust cue"
                value={confidencePercent > 80 ? "Strong" : confidencePercent > 60 ? "Moderate" : "Low"}
                helper="A quick read on how decisive the model output appears."
              />
              <InsightCard
                icon={Bot}
                label="Interpretation"
                value={analysisType === "topic" ? "Aggregated" : "Single item"}
                helper={analysisType === "topic" ? "Based on a topic summary." : "Based on one piece of content."}
              />
            </div>

            <div className="rounded-2xl border border-dashed border-white/10 bg-black/15 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/35">Source preview</p>
              <p className="mt-2 text-sm leading-relaxed text-white/60">
                {sourceDetail || "Run an analysis to populate this panel with source context and supporting details."}
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
