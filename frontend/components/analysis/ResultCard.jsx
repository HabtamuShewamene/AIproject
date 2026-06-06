"use client";
import { useState } from "react";
import {
  CheckCheck,
  Copy,
  Eye,
  Globe,
  Hash,
  Heart,
  Languages,
  MessageCircle,
  Minus,
  Repeat2,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react";
import Badge from "@/components/ui/Badge";
import SentimentGauge from "./SentimentGauge";
import ConfidenceBar from "./ConfidenceBar";
import { formatCount, formatScore, truncate } from "@/utils/formatters";

export default function ResultCard({ result }) {
  const [copied, setCopied] = useState(false);
  const [showAllPosts, setShowAllPosts] = useState(false);
  const [selectedPostIndex, setSelectedPostIndex] = useState(0);

  if (!result) return null;

  const {
    analysisType,
    topic,
    sentiment,
    confidence,
    original_text,
    translated_text,
    language,
    metrics,
    summary,
    total_tweets,
    results,
  } = result;

  const showTranslated =
    translated_text &&
    original_text &&
    translated_text.trim().toLowerCase() !== original_text.trim().toLowerCase();

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const engagementMetrics = [
    { icon: Heart, label: "Likes", value: metrics?.likes, color: "#f87171" },
    { icon: Repeat2, label: "Retweets", value: metrics?.retweets, color: "#00F5A0" },
    { icon: MessageCircle, label: "Replies", value: metrics?.replies, color: "#60a5fa" },
    { icon: Eye, label: "Views", value: metrics?.views, color: "#c084fc" },
  ].filter((metric) => metric.value !== null && metric.value !== undefined);

  const topicBreakdown = analysisType === "topic"
    ? [
        { icon: TrendingUp, label: "Positive", value: `${summary?.positive ?? 0}%`, color: "#00F5A0" },
        { icon: TrendingDown, label: "Negative", value: `${summary?.negative ?? 0}%`, color: "#f87171" },
        { icon: Minus, label: "Neutral", value: `${summary?.neutral ?? 0}%`, color: "#facc15" },
        {
          icon: Users,
          label: "Posts analyzed",
          value: formatCount(total_tweets ?? summary?.total ?? 0),
          color: "#60a5fa",
        },
      ]
    : [];

  const topicPosts = analysisType === "topic" && Array.isArray(results) ? results : [];
  const samplePosts = showAllPosts ? topicPosts : topicPosts.slice(0, 5);
  const selectedPost = topicPosts[selectedPostIndex] || null;

  const formatPostMeta = (value, fallback = "—") => (value || value === 0 ? value : fallback);

  return (
    <div className="glass-card p-5 space-y-4" id="results-section">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <h3 className="font-bold text-white text-lg">Analysis Result</h3>
          <Badge sentiment={sentiment} />
        </div>
        <button
          id="copy-result-btn"
          onClick={handleCopy}
          className="flex items-center gap-2 text-xs text-white/40 hover:text-[#00F5A0] transition-colors px-3 py-1.5 rounded-lg border border-white/10 hover:border-[#00F5A0]/30"
        >
          {copied ? <CheckCheck size={13} className="text-[#00F5A0]" /> : <Copy size={13} />}
          {copied ? "Copied!" : "Copy JSON"}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-5 items-center">
        <SentimentGauge score={confidence ?? 0} sentiment={(sentiment || "neutral").toLowerCase()} />
        <div className="space-y-4 min-w-0">
          <ConfidenceBar score={confidence ?? 0} />
          {analysisType === "topic" ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-white/50">
                <Hash size={14} />
                <span>
                  Topic: <span className="text-white/80 font-semibold">{topic}</span>
                </span>
              </div>
              <p className="text-sm text-white/45">
                Dominant sentiment share: <span className="text-white/75 font-semibold">{formatScore(confidence)}</span>
              </p>
            </div>
          ) : (
            language && (
              <div className="flex items-center gap-2 text-sm text-white/50">
                <Globe size={14} />
                <span>
                  Detected language: <span className="text-white/80 font-semibold">{language.toUpperCase()}</span>
                </span>
              </div>
            )
          )}
        </div>
      </div>

      {analysisType === "topic" && topicBreakdown.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {topicBreakdown.map(({ icon: Icon, label, value, color }) => (
            <div
              key={label}
              className="p-3 rounded-lg bg-white/[0.03] border border-white/5 flex items-center gap-3"
            >
              <Icon size={15} style={{ color }} className="shrink-0" />
              <div>
                <span className="block text-base font-bold font-mono text-white leading-none">{value}</span>
                <span className="text-[10px] text-white/35 uppercase tracking-wide">{label}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {analysisType === "topic" && Number(total_tweets ?? summary?.total ?? 0) === 0 && (
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
          No posts were found for this topic. Try a broader keyword or confirm the scraper returned results.
        </div>
      )}

      {original_text && (
        <div className="space-y-2">
          <p className="text-xs text-white/35 uppercase tracking-wider font-medium">Original Text</p>
          <p className="text-sm text-white/75 leading-relaxed p-3 rounded-lg bg-white/[0.03] border border-white/5 font-mono whitespace-pre-wrap">
            {original_text}
          </p>
        </div>
      )}

      {showTranslated && (
        <div className="space-y-2">
          <p className="text-xs text-white/35 uppercase tracking-wider font-medium flex items-center gap-1.5">
            <Languages size={12} /> Translated Text
          </p>
          <p className="text-sm text-white/65 leading-relaxed p-3 rounded-lg bg-[#7C3AED]/5 border border-[#7C3AED]/15 whitespace-pre-wrap">
            {translated_text}
          </p>
        </div>
      )}

      {analysisType === "topic" && topicPosts.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <p className="text-xs text-white/35 uppercase tracking-wider font-medium">Sample Posts</p>
            <div className="flex items-center gap-3">
              <p className="text-xs text-white/30">
                {showAllPosts ? `${topicPosts.length} posts shown` : `Showing 5 of ${topicPosts.length}`}
              </p>
              {topicPosts.length > 5 && (
                <button
                  type="button"
                  onClick={() => setShowAllPosts((prev) => !prev)}
                  className="text-xs px-3 py-1.5 rounded-lg border border-white/10 text-white/70 hover:text-white hover:border-[#00F5A0]/30 transition-colors"
                >
                  {showAllPosts ? "Show less" : "More posts"}
                </button>
              )}
            </div>
          </div>
          <div className="grid gap-3 lg:grid-cols-[1fr_0.95fr]">
            <div className="grid gap-2">
              {samplePosts.map((item, index) => {
                const absoluteIndex = showAllPosts ? index : index;
                const isSelected = selectedPostIndex === absoluteIndex && selectedPost?.url === item.url;

                return (
                  <button
                    key={`${item.url || item.text}-${index}`}
                    type="button"
                    onClick={() => setSelectedPostIndex(showAllPosts ? index : index)}
                    className={`text-left rounded-lg border p-3 space-y-2 transition-colors ${
                      isSelected
                        ? "border-[#00F5A0]/40 bg-[#00F5A0]/8"
                        : "border-white/8 bg-white/[0.03] hover:border-white/15"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-2 text-xs text-white/50">
                        <Hash size={12} />
                        <span>{item.author ? `@${item.author}` : "Unknown author"}</span>
                      </div>
                      <Badge sentiment={item.sentiment} />
                    </div>
                    <p className="text-sm text-white/70 leading-relaxed">{truncate(item.text, 180)}</p>
                    <div className="flex items-center gap-4 flex-wrap text-xs text-white/40">
                      <span>Confidence {formatScore(item.confidence)}</span>
                      <span>Likes {formatCount(item.likes)}</span>
                      <span>Replies {formatCount(item.replies)}</span>
                      <span>Retweets {formatCount(item.retweets)}</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {selectedPost ? (
              <div className="rounded-lg border border-white/8 bg-white/[0.03] p-4 space-y-3">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-2 text-xs text-white/50">
                    <Hash size={12} />
                    <span>{selectedPost.author ? `@${selectedPost.author}` : "Unknown author"}</span>
                  </div>
                  <Badge sentiment={selectedPost.sentiment} />
                </div>

                <div className="space-y-2">
                  <p className="text-xs text-white/35 uppercase tracking-wider font-medium">Post URL</p>
                  <a
                    href={selectedPost.url || "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="block text-sm text-[#00F5A0] break-all hover:underline"
                  >
                    {formatPostMeta(selectedPost.url, "No URL available")}
                  </a>
                </div>

                <div className="space-y-2">
                  <p className="text-xs text-white/35 uppercase tracking-wider font-medium">Full Post</p>
                  <p className="text-sm text-white/75 leading-relaxed whitespace-pre-wrap">
                    {selectedPost.text || "No text available"}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Created</p>
                    <p className="mt-1 text-sm text-white/80">{formatPostMeta(selectedPost.created_at)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Language</p>
                    <p className="mt-1 text-sm text-white/80">{formatPostMeta(selectedPost.language)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Media</p>
                    <p className="mt-1 text-sm text-white/80">{formatPostMeta(selectedPost.media_type)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Bookmarked</p>
                    <p className="mt-1 text-sm text-white/80">{formatCount(selectedPost.bookmarks)}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Likes</p>
                    <p className="mt-1 text-sm text-white/80">{formatCount(selectedPost.likes)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Retweets</p>
                    <p className="mt-1 text-sm text-white/80">{formatCount(selectedPost.retweets)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Replies</p>
                    <p className="mt-1 text-sm text-white/80">{formatCount(selectedPost.replies)}</p>
                  </div>
                  <div className="rounded-lg bg-black/20 border border-white/5 p-3">
                    <p className="text-[10px] uppercase tracking-wide text-white/35">Quotes</p>
                    <p className="mt-1 text-sm text-white/80">{formatCount(selectedPost.quotes)}</p>
                  </div>
                </div>

                {Array.isArray(selectedPost.hashtags) && selectedPost.hashtags.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs text-white/35 uppercase tracking-wider font-medium">Hashtags</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedPost.hashtags.map((tag) => (
                        <span key={tag} className="text-xs px-2 py-1 rounded-full bg-white/5 border border-white/10 text-white/70">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}

      {analysisType !== "topic" && engagementMetrics.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {engagementMetrics.map(({ icon: Icon, label, value, color }) => (
            <div
              key={label}
              className="p-3 rounded-lg bg-white/[0.03] border border-white/5 flex items-center gap-3"
            >
              <Icon size={15} style={{ color }} />
              <div>
                <span className="block text-base font-bold font-mono text-white leading-none">{formatCount(value)}</span>
                <span className="text-[10px] text-white/35 uppercase tracking-wide">{label}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
