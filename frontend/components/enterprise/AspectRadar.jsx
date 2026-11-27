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
      <div className="glass-card p-4 text-center text-xs text-[#71767B]">
        No department-specific aspects detected. The feedback represents general sentiment.
      </div>
    );
  }

  const getPolarityStyle = (polarity) => {
    switch (polarity) {
      case "positive":
        return {
          bg: "bg-[#16A36A]/10",
          border: "border-[#16A36A]/30",
          text: "text-[#16A36A]",
          bar: "#16A36A",
          icon: CheckCircle2,
        };
      case "negative":
        return {
          bg: "bg-[#D65353]/10",
          border: "border-[#D65353]/30",
          text: "text-[#D65353]",
          bar: "#D65353",
          icon: AlertCircle,
        };
      default:
        return {
          bg: "bg-[#71767B]/10",
          border: "border-[#71767B]/30",
          text: "text-[#71767B]",
          bar: "#71767B",
          icon: MinusCircle,
        };
    }
  };

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
          <Zap size={15} className="text-[#1D9BF0]" />
          Aspect-Based Sentiment Breakdown
        </h3>
        <span className="text-[11px] text-[#71767B] font-mono">
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
                  <span className="p-1.5 rounded-lg bg-[#090D12] text-white/80 border border-[#202A36]">
                    <AspectIcon size={14} />
                  </span>
                  <span className="text-xs font-semibold text-white">{item.label}</span>
                </div>
                <span className={`flex items-center gap-1 text-[11px] font-semibold capitalize ${style.text}`}>
                  <PolarityIcon size={12} />
                  {item.polarity}
                </span>
              </div>

              {/* Intensity progress track */}
              <div className="space-y-1">
                <div className="h-1.5 w-full bg-[#090D12] rounded-full overflow-hidden border border-[#202A36]">
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
                      className="px-2 py-0.5 rounded-full text-[10px] bg-[#090D12] text-[#8899A6] border border-[#202A36] font-mono"
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
