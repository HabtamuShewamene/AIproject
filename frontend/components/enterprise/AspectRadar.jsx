"use client";
import { Package, Headphones, CreditCard, Zap, Truck, CheckCircle2, AlertCircle, MinusCircle } from "lucide-react";

const ICON_MAP = {
  Package,
  Headphones,
  CreditCard,
  Zap,
  Truck,
};

export default function AspectRadar({ aspects }) {
  if (!aspects || aspects.length === 0) {
    return (
      <div className="glass-card p-4 text-center text-xs text-white/40">
        No department-specific aspects detected. The feedback represents general sentiment.
      </div>
    );
  }

  const getPolarityStyle = (polarity) => {
    switch (polarity) {
      case "positive":
        return {
          bg: "bg-[#00F5A0]/10",
          border: "border-[#00F5A0]/30",
          text: "text-[#00F5A0]",
          bar: "#00F5A0",
          icon: CheckCircle2,
        };
      case "negative":
        return {
          bg: "bg-[#f87171]/10",
          border: "border-[#f87171]/30",
          text: "text-[#f87171]",
          bar: "#f87171",
          icon: AlertCircle,
        };
      default:
        return {
          bg: "bg-[#facc15]/10",
          border: "border-[#facc15]/30",
          text: "text-[#facc15]",
          bar: "#facc15",
          icon: MinusCircle,
        };
    }
  };

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white/80 flex items-center gap-2">
          <Zap size={15} className="text-[#00F5A0]" />
          Aspect-Based Sentiment Breakdown
        </h3>
        <span className="text-[11px] text-white/40 font-mono">
          {aspects.length} aspect{aspects.length > 1 ? "s" : ""} evaluated
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {aspects.map((item) => {
          const style = getPolarityStyle(item.polarity);
          const AspectIcon = ICON_MAP[item.icon] || Zap;
          const PolarityIcon = style.icon;
          const pct = Math.min(100, Math.max(10, Math.round(Math.abs(item.score || 0.75) * 100)));

          return (
            <div
              key={item.aspect_id}
              className={`p-3.5 rounded-xl border ${style.border} ${style.bg} space-y-2.5 transition-all`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-black/40 text-white/80">
                    <AspectIcon size={14} />
                  </span>
                  <span className="text-xs font-semibold text-white/90">{item.label}</span>
                </div>
                <span className={`flex items-center gap-1 text-[11px] font-semibold capitalize ${style.text}`}>
                  <PolarityIcon size={12} />
                  {item.polarity}
                </span>
              </div>

              {/* Intensity progress track */}
              <div className="space-y-1">
                <div className="h-1.5 w-full bg-black/30 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${pct}%`, background: style.bar }}
                  />
                </div>
              </div>

              {/* Matched keywords pills */}
              {item.matched_keywords && item.matched_keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {item.matched_keywords.map((kw) => (
                    <span
                      key={kw}
                      className="px-2 py-0.5 rounded-full text-[10px] bg-black/30 text-white/60 font-mono"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
