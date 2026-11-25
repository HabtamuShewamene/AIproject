const COLORS = {
  positive: { bg: "#00F5A020", text: "#00F5A0", border: "#00F5A040" },
  negative: { bg: "#f8717120", text: "#f87171", border: "#f8717140" },
  neutral:  { bg: "#facc1520", text: "#facc15", border: "#facc1540" },
  uncertain:{ bg: "#94a3b820", text: "#94a3b8", border: "#94a3b840" },
};

export default function Badge({ sentiment }) {
  const s = (sentiment || "neutral").toLowerCase();
  const c = COLORS[s] || COLORS.neutral;
  return (
    <span
      className="px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize"
      style={{ background: c.bg, color: c.text, border: `1px solid ${c.border}` }}
      aria-label={`Sentiment: ${s}`}
    >
      {s}
    </span>
  );
}
