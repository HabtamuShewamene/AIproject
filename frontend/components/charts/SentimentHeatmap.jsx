"use client";

import { Fragment, useMemo, useState } from "react";
import ChartCard from "./ChartCard";

const SENTIMENTS = [
  { key: "positive", label: "Positive", color: "0, 245, 160" },
  { key: "negative", label: "Negative", color: "248, 113, 113" },
  { key: "neutral", label: "Neutral", color: "250, 204, 21" },
];

function buildTimeline(history = []) {
  const buckets = new Map();

  history.forEach((entry) => {
    if (!entry?.date) {
      return;
    }

    const date = new Date(entry.date);

    if (Number.isNaN(date.getTime())) {
      return;
    }

    const dateKey = date.toISOString().slice(0, 10);
    const label = new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
    const sentiment = (entry.sentiment || "neutral").toLowerCase();

    if (!SENTIMENTS.some((item) => item.key === sentiment)) {
      return;
    }

    const bucket = buckets.get(dateKey) || {
      key: dateKey,
      label,
      positive: { count: 0, confidenceTotal: 0 },
      negative: { count: 0, confidenceTotal: 0 },
      neutral: { count: 0, confidenceTotal: 0 },
      total: 0,
      latest: date.getTime(),
    };

    bucket[sentiment].count += 1;
    bucket[sentiment].confidenceTotal += toPercentConfidence(entry.confidence);
    bucket.total += 1;
    bucket.latest = Math.max(bucket.latest, date.getTime());

    buckets.set(dateKey, bucket);
  });

  const dates = Array.from(buckets.values())
    .sort((a, b) => a.latest - b.latest)
    .slice(-14)
    .map((item) => ({ key: item.key, label: item.label }));

  const cells = SENTIMENTS.map((sentiment) => ({
    ...sentiment,
    cells: dates.map((date) => {
      const bucket = buckets.get(date.key);
      const data = bucket?.[sentiment.key] || { count: 0, confidenceTotal: 0 };
      const averageConfidence = data.count > 0 ? data.confidenceTotal / data.count : 0;

      return {
        dateKey: date.key,
        dateLabel: date.label,
        sentiment: sentiment.key,
        count: data.count,
        confidence: averageConfidence,
      };
    }),
  }));

  return { dates, rows: cells };
}

function toPercentConfidence(value) {
  const confidence = Number(value ?? 0);
  return confidence <= 1 ? confidence * 100 : confidence;
}

function getAlpha(count, confidence) {
  const normalizedCount = Math.min(1, count / 4);
  const normalizedConfidence = Math.min(1, confidence / 100);
  return 0.12 + normalizedCount * 0.46 + normalizedConfidence * 0.22;
}

function CellTooltip({ cell }) {
  if (!cell) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-white/45">
        Hover a cell to inspect daily sentiment intensity.
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-white/70">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs uppercase tracking-[0.18em] text-white/35">Heatmap detail</span>
        <span className="text-xs text-white/45">{cell.dateLabel}</span>
      </div>
      <p className="mt-2 text-base font-semibold text-white capitalize">{cell.sentiment}</p>
      <p className="mt-1 text-white/55">Activity count: {cell.count}</p>
      <p className="mt-1 text-white/55">Average confidence: {Math.round(cell.confidence)}%</p>
    </div>
  );
}

export default function SentimentHeatmap({ history }) {
  const [activeCell, setActiveCell] = useState(null);

  const { dates, rows } = useMemo(() => buildTimeline(history), [history]);
  const empty = dates.length === 0;

  return (
    <ChartCard
      title="Sentiment Timeline Heatmap"
      description="Sentiment activity intensity grouped by day and sentiment class."
      empty={empty}
    >
      {empty ? null : (
        <div className="space-y-4">
          <div className="overflow-x-auto">
            <div className="min-w-[760px] rounded-2xl border border-white/10 bg-white/[0.02] p-3">
              <div
                className="grid gap-2"
                style={{ gridTemplateColumns: `120px repeat(${dates.length}, minmax(46px, 1fr))` }}
              >
                <div className="px-2 py-2 text-xs uppercase tracking-[0.18em] text-white/35">Sentiment</div>
                {dates.map((date) => (
                  <div key={date.key} className="px-1 py-2 text-center text-[11px] uppercase tracking-[0.12em] text-white/35">
                    {date.label}
                  </div>
                ))}

                {rows.map((row) => (
                  <Fragment key={row.key}>
                    <div key={`${row.key}-label`} className="flex items-center px-2 text-sm font-medium text-white/65 capitalize">
                      <span
                        className="mr-2 h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: `rgb(${row.color})` }}
                      />
                      {row.label}
                    </div>
                    {row.cells.map((cell) => {
                      const alpha = getAlpha(cell.count, cell.confidence);

                      return (
                        <button
                          key={`${row.key}-${cell.dateKey}`}
                          type="button"
                          onMouseEnter={() => setActiveCell(cell)}
                          onFocus={() => setActiveCell(cell)}
                          onMouseLeave={() => setActiveCell(null)}
                          onBlur={() => setActiveCell(null)}
                          className="group h-12 rounded-xl border border-white/5 transition-transform duration-150 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-[#00F5A0]/30"
                          style={{
                            backgroundColor: `rgba(${row.color}, ${alpha})`,
                          }}
                          aria-label={`${row.label} on ${cell.dateLabel}: ${cell.count} entries`}
                        >
                          <div className="flex h-full flex-col items-center justify-center text-[11px] font-semibold text-white/90">
                            <span>{cell.count > 0 ? cell.count : ""}</span>
                            <span className="text-[10px] text-white/55">{cell.count > 0 ? `${Math.round(cell.confidence)}%` : ""}</span>
                          </div>
                        </button>
                      );
                    })}
                  </Fragment>
                ))}
              </div>
            </div>
          </div>

          <div className="grid gap-3 xl:grid-cols-[1fr_280px]">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.18em] text-white/35">
                <span>Intensity</span>
                <span className="inline-flex items-center gap-2 lowercase tracking-normal text-white/45">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#00F5A0]" /> Positive
                </span>
                <span className="inline-flex items-center gap-2 lowercase tracking-normal text-white/45">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#f87171]" /> Negative
                </span>
                <span className="inline-flex items-center gap-2 lowercase tracking-normal text-white/45">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#facc15]" /> Neutral
                </span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-white/50">
                Brighter cells indicate a higher activity count and stronger average confidence for that sentiment bucket.
              </p>
            </div>
            <CellTooltip cell={activeCell} />
          </div>
        </div>
      )}
    </ChartCard>
  );
}
