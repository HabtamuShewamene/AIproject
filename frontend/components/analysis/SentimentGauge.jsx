export default function SentimentGauge({ score, sentiment }) {
  const colors = { positive: "#00F5A0", negative: "#f87171", neutral: "#facc15", uncertain: "#94a3b8" };
  const color = colors[sentiment] || "#60a5fa";
  const pct = Math.round((score || 0) * 100);

  return (
    <div className="flex flex-col items-center gap-2" aria-label={`Confidence gauge: ${pct}%`}>
      <svg width="120" height="70" viewBox="0 0 120 70" aria-hidden="true">
        {/* Track */}
        <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" strokeLinecap="round" />
        {/* Fill */}
        <path
          d="M 10 65 A 50 50 0 0 1 110 65"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * 157} 157`}
        />
      </svg>
      <span className="text-2xl font-bold font-mono" style={{ color }}>{pct}%</span>
      <span className="text-xs text-white/40 capitalize">{sentiment}</span>
    </div>
  );
}
