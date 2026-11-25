export default function ConfidenceBar({ score }) {
  const pct = Math.round((score || 0) * 100);
  const color = pct >= 90 ? "#00F5A0" : pct >= 70 ? "#facc15" : pct >= 45 ? "#fb923c" : "#f87171";

  return (
    <div>
      <div className="flex justify-between text-xs text-white/50 mb-1">
        <span>Confidence</span>
        <span className="font-mono">{pct}%</span>
      </div>
      <div
        className="h-2 rounded-full bg-white/10 overflow-hidden"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${pct}% confidence`}
      >
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}
