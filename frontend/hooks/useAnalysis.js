"use client";
import { useState, useCallback } from "react";
import { analyzeTwitterPost, analyzeCustomText, analyzeTopic } from "@/services/api";
import useHistory from "@/hooks/useHistory";

export default function useAnalysis() {
  const [loading, setLoading]   = useState(false);
  const [result,  setResult]    = useState(null);
  const [error,   setError]     = useState(null);
  const { history, addEntry } = useHistory();

  const _run = useCallback(async (apiFn, type, inputPreview) => {
    setLoading(true);
    setError(null);
    // Don't clear result yet — keep it visible while loading
    try {
      const data = await apiFn();
      const normalised = normalise(data, type);
      setResult(normalised);
      addEntry({
        type,
        sentiment:    normalised.sentiment,
        confidence:   normalised.confidence,
        inputPreview: inputPreview.slice(0, 80),
        date:         new Date().toISOString(),
        topic:        normalised.topic || null,
        summary:      normalised.summary || null,
        totalTweets:   normalised.total_tweets || null,
      });
    } catch (err) {
      setResult(null);
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [addEntry]);

  const runTwitterAnalysis = useCallback((url) => {
    _run(() => analyzeTwitterPost(url), "URL", url);
  }, [_run]);

  const runTextAnalysis = useCallback((text) => {
    _run(() => analyzeCustomText(text), "Text", text);
  }, [_run]);

  const runTopicAnalysis = useCallback((query) => {
    _run(() => analyzeTopic(query), "Topic", query);
  }, [_run]);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    loading,
    result,
    error,
    history,
    runTwitterAnalysis,
    runTextAnalysis,
    runTopicAnalysis,
    clearResult,
  };
}

// ── Shape normaliser ──────────────────────────────────────
// /analyze-twitter and /predict return slightly different shapes.
// Unify them so ResultCard always receives the same structure.
function normalise(data, type) {
  if (data?.error) {
    throw new Error(data.error);
  }

  if (type === "Topic") {
    const summary = data.summary || {};
    const totalTweets = Number(data.total_tweets ?? summary.total ?? 0);

    if (totalTweets <= 0) {
      return {
        success: true,
        analysisType: "topic",
        topic: data.query,
        query: data.query,
        sentiment: "neutral",
        confidence: 0,
        summary: {
          total: 0,
          positive: 0,
          negative: 0,
          neutral: 0,
        },
        total_tweets: 0,
        results: [],
        intelligence: data.intelligence || null,
        metrics: null,
        original_text: null,
        translated_text: null,
        language: null,
        empty: true,
      };
    }

    const sentimentBreakdown = [
      { label: "positive", value: Number(summary.positive ?? 0) },
      { label: "negative", value: Number(summary.negative ?? 0) },
      { label: "neutral", value: Number(summary.neutral ?? 0) },
    ];
    const dominant = sentimentBreakdown.sort((a, b) => b.value - a.value)[0] || {
      label: "neutral",
      value: 0,
    };

    return {
      success: true,
      analysisType: "topic",
      topic: data.query,
      query: data.query,
      sentiment: dominant.label,
      confidence: dominant.value / 100,
      summary: {
        total: Number(summary.total ?? totalTweets),
        positive: Number(summary.positive ?? 0),
        negative: Number(summary.negative ?? 0),
        neutral: Number(summary.neutral ?? 0),
      },
      total_tweets: totalTweets,
      results: Array.isArray(data.results) ? data.results : [],
      intelligence: data.intelligence || null,
      metrics: null,
      original_text: null,
      translated_text: null,
      language: null,
    };
  }

  if (type === "URL") {
    return {
      success: true,
      analysisType: "url",
      sentiment: data.sentiment,
      confidence: data.confidence,
      language: data.language || null,
      original_text: data.tweet_text || data.original_text || data.text || null,
      translated_text: data.translated_text || null,
      intelligence: data.intelligence || null,
      metrics: {
        likes: data.metrics?.likes ?? null,
        retweets: data.metrics?.retweets ?? null,
        replies: data.metrics?.replies ?? null,
        quotes: data.metrics?.quotes ?? null,
      },
    };
  }

  return {
    success: true,
    analysisType: "text",
    sentiment: data.sentiment,
    confidence: data.confidence,
    language: data.language || null,
    original_text: data.original_text || data.text || null,
    translated_text: data.translated_text || null,
    intelligence: data.intelligence || null,
    metrics: null,
  };
}
