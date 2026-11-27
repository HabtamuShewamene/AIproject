"use client";
import { useState } from "react";
import { Upload, FileText, Download, Filter, Search, CheckCircle, AlertTriangle, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const PRELOADED_DATASETS = [
  {
    name: "SaaS Feedback & Churn Risk",
    description: "10 enterprise customer reviews covering billing, bugs, and praise",
    texts: [
      "The platform performance is outstanding and blazingly fast!",
      "I was double-charged on my credit card and nobody in billing is replying. Fix this immediately or I am canceling!",
      "Great user interface, but the CSV export feature crashed twice this morning.",
      "Customer support agent Sarah was incredibly patient and resolved our integration ticket in 10 minutes.",
      "Terrible pricing increase with zero prior notice. We are migrating our entire team to a competitor next month.",
      "The new analytics dashboard gives our executives exactly what they need every Monday.",
      "API response time has degraded significantly over the last 48 hours. Please look into this.",
      "We love this software! It has saved our marketing team at least 15 hours every single week.",
      "Constant sync errors on mobile. Unusable when traveling.",
      "Standard product, does what it says on the tin without issues.",
    ],
  },
  {
    name: "Airline Flight Delay Tweets",
    description: "10 passenger social posts covering cancellations, luggage, and gates",
    texts: [
      "Flight 402 delayed 5 hours with zero gate updates and no water vouchers. Absolutely disgusting service!",
      "Thank you to the flight crew on today's flight to Chicago for being so courteous and cheerful!",
      "Lost my checked baggage containing vital business documents. Customer desk is completely deserted.",
      "Smooth boarding, on-time departure, and WiFi worked flawlessly the entire flight.",
      "Canceled my return leg without notifying me! Missed my sister's wedding because of you.",
      "Flight attendants handled the severe turbulence like absolute pros. Felt very safe.",
      "Dirty seats, broken tray table, and reading light didn't work for a 6 hour cross-country flight.",
      "Quick turn-around at the gate despite the winter storm. Kudos to the ground operations team!",
      "Seat pitch in economy is completely inhumane for anyone over six feet tall.",
      "Normal flight. Arrived 5 minutes early.",
    ],
  },
  {
    name: "Consumer Electronics Launch",
    description: "10 flagship device reviews covering camera, battery, and price",
    texts: [
      "The low-light camera capabilities completely demolish anything else on the market!",
      "Battery life drops from 100% to 20% in just 4 hours of light screen time. Unacceptable defect.",
      "Build quality is solid and premium, but $1,400 is an absurdly high price tag.",
      "Haptic feedback feels incredible and the 120Hz display is butter smooth.",
      "Overheating issue during simple 4K video recording. Phone literally shut down after 8 minutes.",
      "Speaker volume is loud and clear with surprising bass response.",
      "Screen scratched on day two despite being kept in an empty pocket.",
      "Fast charging delivers 0 to 80% in under 25 minutes. Game changer for travel.",
      "Software bloatware preinstalled is ridiculous for an unlocked flagship phone.",
      "Average phone, decent upgrade if you are coming from a 4-year-old device.",
    ],
  },
];

export default function BatchDataHub({ onSelectRowForCopilot }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterSentiment, setFilterSentiment] = useState("all");
  const [summary, setSummary] = useState(null);

  const processTexts = async (textsArray) => {
    setLoading(true);
    setProgress(15);
    try {
      const res = await fetch(`${API}/api/v1/predict/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texts: textsArray.slice(0, 50) }),
      });
      setProgress(75);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Batch prediction failed");

      setItems(data.predictions);
      setSummary(data.summary);
      setProgress(100);
    } catch (err) {
      alert(`Error processing batch: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content !== "string") return;
      const lines = content
        .split(/\r?\n/)
        .map((l) => l.trim().replace(/^["']|["']$/g, ""))
        .filter((l) => l.length >= 3);
      if (lines.length > 0) {
        processTexts(lines);
      } else {
        alert("No valid text lines found in file.");
      }
    };
    reader.readAsText(file);
  };

  const handleExportCSV = () => {
    if (items.length === 0) return;
    const header = ["Text", "Sentiment", "Confidence", "Urgency", "Intent", "Aspects"];
    const rows = items.map((p) => {
      const aspectsStr = (p.aspects || []).map((a) => a.label).join("; ");
      const triage = p.triage || {};
      return [
        `"${(p.text || "").replace(/"/g, '""')}"`,
        p.sentiment,
        (p.confidence * 100).toFixed(1) + "%",
        triage.urgency || "Standard",
        `"${triage.intent || ""}"`,
        `"${aspectsStr}"`,
      ];
    });

    const csvContent = [header.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `X_Intelligence_Enriched_Batch_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredItems = items.filter((item) => {
    const matchesSearch = item.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSentiment = filterSentiment === "all" || item.sentiment === filterSentiment;
    return matchesSearch && matchesSentiment;
  });

  return (
    <div className="space-y-6">
      {/* Upload & Presets Card */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Upload size={18} className="text-[#1D9BF0]" />
              Batch Ingestion & File Intelligence Hub
            </h2>
            <p className="text-xs text-[#71767B]">
              Drag-and-drop CSV datasets or load pre-curated enterprise complaint benchmarks.
            </p>
          </div>

          <label className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#1D9BF0] text-white font-semibold text-xs cursor-pointer hover:bg-[#1A8CD8] transition-all">
            <Upload size={14} />
            <span>Upload CSV Dataset</span>
            <input type="file" accept=".csv,.txt" onChange={handleFileUpload} className="hidden" />
          </label>
        </div>

        {/* Preloaded buttons */}
        <div className="pt-2 border-t border-[#202A36] space-y-2">
          <span className="text-[11px] text-[#71767B] uppercase tracking-wider font-semibold">
            One-Click Enterprise Benchmarks
          </span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PRELOADED_DATASETS.map((ds, idx) => (
              <button
                key={idx}
                disabled={loading}
                onClick={() => processTexts(ds.texts)}
                className="p-3 rounded-xl bg-[#090D12] hover:bg-[#151C25] border border-[#202A36] hover:border-[#1D9BF0]/40 text-left transition-all space-y-1"
              >
                <div className="text-xs font-bold text-white flex items-center justify-between">
                  <span>📊 {ds.name}</span>
                  <span className="text-[10px] text-[#1D9BF0] font-mono">10 rows</span>
                </div>
                <p className="text-[11px] text-[#71767B] line-clamp-1">{ds.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Progress Bar */}
        {loading && (
          <div className="space-y-1.5 pt-2">
            <div className="flex justify-between text-xs text-[#8899A6]">
              <span>Vectorizing & inferencing batch...</span>
              <span>{progress}%</span>
            </div>
            <div className="h-2 w-full bg-[#090D12] rounded-full overflow-hidden border border-[#202A36]">
              <div
                className="h-full bg-[#1D9BF0] transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Summary KPI Bar */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="glass-card p-4 text-center">
            <span className="text-[10px] text-[#71767B] uppercase">Total Items</span>
            <p className="text-xl font-bold font-mono text-white mt-0.5">{items.length}</p>
          </div>
          <div className="glass-card p-4 text-center border-b-2 border-b-[#16A36A]">
            <span className="text-[10px] text-[#71767B] uppercase">Positive Ratio</span>
            <p className="text-xl font-bold font-mono text-[#16A36A] mt-0.5">{summary.positive || 0}%</p>
          </div>
          <div className="glass-card p-4 text-center border-b-2 border-b-[#D65353]">
            <span className="text-[10px] text-[#71767B] uppercase">Negative Ratio</span>
            <p className="text-xl font-bold font-mono text-[#D65353] mt-0.5">{summary.negative || 0}%</p>
          </div>
          <div className="glass-card p-4 text-center border-b-2 border-b-[#71767B]">
            <span className="text-[10px] text-[#71767B] uppercase">Neutral Ratio</span>
            <p className="text-xl font-bold font-mono text-[#71767B] mt-0.5">{summary.neutral || 0}%</p>
          </div>
        </div>
      )}

      {/* Filter and Table */}
      {items.length > 0 && (
        <div className="glass-card p-5 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-3">
            {/* Search */}
            <div className="flex items-center gap-2 bg-[#090D12] border border-[#202A36] rounded-lg px-3 py-1.5 text-xs text-white w-64">
              <Search size={14} className="text-[#71767B]" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search feedback keywords..."
                className="bg-transparent outline-none flex-1 placeholder-[#71767B]/60 text-xs text-white"
              />
            </div>

            {/* Filter buttons */}
            <div className="flex items-center gap-1.5 flex-wrap">
              {["all", "positive", "negative", "neutral"].map((s) => (
                <button
                  key={s}
                  onClick={() => setFilterSentiment(s)}
                  className={`px-3 py-1 rounded-lg text-xs capitalize transition-all ${
                    filterSentiment === s
                      ? "bg-[#1D9BF0] text-white font-semibold"
                      : "bg-[#090D12] text-[#71767B] hover:text-white border border-[#202A36]"
                  }`}
                >
                  {s}
                </button>
              ))}

              <button
                onClick={handleExportCSV}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#090D12] hover:bg-[#1D9BF0] hover:text-white text-[#8899A6] text-xs font-semibold transition-all border border-[#202A36]"
              >
                <Download size={13} />
                <span>Export CSV</span>
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-lg border border-[#202A36]">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090D12] text-[#71767B] border-b border-[#202A36] uppercase text-[10px] font-mono">
                <tr>
                  <th className="py-2.5 px-3">Feedback Text</th>
                  <th className="py-2.5 px-3">Sentiment</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Urgency & Intent</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202A36] text-[#8899A6]">
                {filteredItems.map((row, idx) => {
                  const triage = row.triage || {};
                  return (
                    <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-3 max-w-xs md:max-w-md truncate text-white">
                        {row.text}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[11px] font-semibold capitalize ${
                            row.sentiment === "positive"
                              ? "bg-[#16A36A]/15 text-[#16A36A]"
                              : row.sentiment === "negative"
                              ? "bg-[#D65353]/15 text-[#D65353]"
                              : "bg-[#71767B]/15 text-[#71767B]"
                          }`}
                        >
                          {row.sentiment}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-white">
                        {(row.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        <span className="text-[#8899A6] font-medium">
                          {triage.urgency || "Standard"}
                        </span>
                        {triage.intent && (
                          <span className="text-[10px] text-[#71767B] block">
                            {triage.intent}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-right whitespace-nowrap">
                        {onSelectRowForCopilot && (
                          <button
                            onClick={() => onSelectRowForCopilot(row)}
                            className="text-[11px] px-2.5 py-1 rounded bg-[#1D9BF0]/15 text-[#1D9BF0] hover:bg-[#1D9BF0]/30 transition-all font-semibold"
                          >
                            Open Copilot →
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
