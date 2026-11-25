"use client";
import { ShieldAlert, AlertTriangle, Info, CheckCircle, ArrowRight } from "lucide-react";

export default function UrgencyBanner({ triage }) {
  if (!triage) return null;

  const { urgency, churn_risk, intent, recommended_action, executive_takeaway } = triage;

  const getUrgencyConfig = (level) => {
    switch (level) {
      case "Critical":
        return {
          border: "border-red-500/40",
          bg: "bg-red-500/10",
          text: "text-red-400",
          badge: "bg-red-500/20 text-red-300 border-red-500/40",
          icon: ShieldAlert,
          title: "Critical Priority Escalation",
        };
      case "High":
        return {
          border: "border-orange-500/40",
          bg: "bg-orange-500/10",
          text: "text-orange-400",
          badge: "bg-orange-500/20 text-orange-300 border-orange-500/40",
          icon: AlertTriangle,
          title: "High Urgency Customer Case",
        };
      case "Medium":
      case "Attention":
        return {
          border: "border-yellow-500/40",
          bg: "bg-yellow-500/10",
          text: "text-yellow-400",
          badge: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40",
          icon: AlertTriangle,
          title: "Operational Attention Required",
        };
      default:
        return {
          border: "border-[#00F5A0]/30",
          bg: "bg-[#00F5A0]/10",
          text: "text-[#00F5A0]",
          badge: "bg-[#00F5A0]/20 text-[#00F5A0] border-[#00F5A0]/40",
          icon: CheckCircle,
          title: "Standard SLA Operational Flow",
        };
    }
  };

  const config = getUrgencyConfig(urgency);
  const IconComponent = config.icon;

  return (
    <div className={`p-4 rounded-xl border ${config.border} ${config.bg} space-y-3 transition-all`}>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <IconComponent size={18} className={config.text} />
          <span className={`text-sm font-bold ${config.text}`}>{config.title}</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {churn_risk && churn_risk !== "None" && (
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
              🚨 Churn Risk: {churn_risk}
            </span>
          )}
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${config.badge}`}>
            Urgency: {urgency}
          </span>
          {intent && (
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-white/10 text-white/80 border border-white/10">
              🏷️ {intent}
            </span>
          )}
        </div>
      </div>

      {executive_takeaway && (
        <p className="text-xs text-white/70 leading-relaxed font-medium">
          {executive_takeaway}
        </p>
      )}

      {recommended_action && (
        <div className="flex items-start gap-2 pt-2 border-t border-white/10 text-xs">
          <span className="text-[#00F5A0] font-semibold flex items-center gap-1 shrink-0">
            <ArrowRight size={13} /> Recommended Action:
          </span>
          <span className="text-white/85">{recommended_action}</span>
        </div>
      )}
    </div>
  );
}
