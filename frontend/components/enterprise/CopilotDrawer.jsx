"use client";
import { useState } from "react";
import { Bot, Sparkles, Send, Copy, Check, MessageSquare, Compass, Shield } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function CopilotDrawer({ activeResult }) {
  const [activeTab, setActiveTab] = useState("drafts"); // 'drafts' | 'chat'
  const [draftType, setDraftType] = useState("empathetic"); // 'empathetic' | 'solution_oriented' | 'executive_brief'
  const [copied, setCopied] = useState(false);

  // Chat state
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I am your SentiAI Copilot. Ask me anything about this customer's feedback, request customized response drafts, or inquire about churn mitigation tactics.",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [loadingChat, setLoadingChat] = useState(false);

  if (!activeResult) {
    return (
      <div className="glass-card p-6 text-center space-y-3">
        <Bot size={28} className="mx-auto text-white/30" />
        <h4 className="text-sm font-semibold text-white/70">AI Copilot Standby</h4>
        <p className="text-xs text-white/40 max-w-sm mx-auto">
          Analyze any text or tweet on the Realtime tab or load a batch dataset to activate conversational insights.
        </p>
      </div>
    );
  }

  const copilot = activeResult.copilot || {};
  const drafts = copilot.drafts || {};
  const drivers = copilot.key_drivers || [];
  const suggestedQueries = copilot.suggested_queries || [
    "What action should we prioritize?",
    "Draft an apology email",
    "Explain why this was classified negative",
  ];

  const currentDraft = drafts[draftType] || "No draft generated.";

  const handleCopy = () => {
    navigator.clipboard.writeText(currentDraft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendMessage = async (msgText) => {
    const query = (msgText || inputMessage).trim();
    if (!query) return;

    const newMessages = [...messages, { role: "user", content: query }];
    setMessages(newMessages);
    setInputMessage("");
    setLoadingChat(true);

    try {
      const res = await fetch(`${API}/api/v1/enterprise/copilot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          analyzed_text: activeResult.text || activeResult.original_text || "",
          sentiment: activeResult.sentiment || "neutral",
          confidence: activeResult.confidence || 0.0,
          triage: activeResult.triage || {},
          aspects: activeResult.aspects || [],
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Copilot query failed");

      setMessages([...newMessages, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: "assistant", content: `⚠️ Error contacting Copilot: ${err.message}` },
      ]);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div className="glass-card p-5 space-y-4">
      {/* Copilot Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[#00F5A0]/15 text-[#00F5A0]">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              SentiAI Copilot
              <span className="px-1.5 py-0.2 rounded text-[9px] bg-[#00F5A0]/20 text-[#00F5A0] font-mono">
                ENTERPRISE
              </span>
            </h3>
            <p className="text-[11px] text-white/40">Conversational Intelligence & Resolution Drafter</p>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex gap-1 p-0.5 rounded-lg bg-black/40 border border-white/10 text-xs">
          <button
            onClick={() => setActiveTab("drafts")}
            className={`px-3 py-1 rounded-md transition-all font-medium ${
              activeTab === "drafts" ? "bg-white/15 text-white" : "text-white/40 hover:text-white"
            }`}
          >
            Resolution Drafts
          </button>
          <button
            onClick={() => setActiveTab("chat")}
            className={`px-3 py-1 rounded-md transition-all font-medium ${
              activeTab === "chat" ? "bg-white/15 text-white" : "text-white/40 hover:text-white"
            }`}
          >
            Interactive Chat
          </button>
        </div>
      </div>

      {/* Key Drivers Banner */}
      {drivers.length > 0 && (
        <div className="p-3 rounded-lg bg-black/25 border border-white/5 space-y-1.5">
          <p className="text-[10px] font-semibold tracking-wider uppercase text-white/40 flex items-center gap-1">
            <Compass size={12} className="text-[#00F5A0]" />
            Key Strategic Drivers
          </p>
          <ul className="text-xs text-white/75 space-y-1">
            {drivers.map((d, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-[#00F5A0] mt-0.5">•</span>
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tab: Resolution Drafts */}
      {activeTab === "drafts" ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex gap-1.5">
              {[
                { id: "empathetic", label: "Empathetic" },
                { id: "solution_oriented", label: "Solution-Oriented" },
                { id: "executive_brief", label: "Executive Brief" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setDraftType(tab.id)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                    draftType === tab.id
                      ? "bg-[#00F5A0] text-black font-semibold"
                      : "bg-white/5 text-white/50 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-all border border-white/10"
            >
              {copied ? <Check size={13} className="text-[#00F5A0]" /> : <Copy size={13} />}
              {copied ? "Copied!" : "Copy Response"}
            </button>
          </div>

          <div className="p-3.5 rounded-xl bg-black/35 border border-white/10 text-xs text-white/80 font-sans leading-relaxed whitespace-pre-wrap select-all">
            {currentDraft}
          </div>
        </div>
      ) : (
        /* Tab: Interactive Chat */
        <div className="space-y-3">
          <div className="h-60 overflow-y-auto space-y-2.5 pr-1 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded-xl max-w-[85%] leading-relaxed ${
                  m.role === "user"
                    ? "ml-auto bg-[#00F5A0]/20 border border-[#00F5A0]/30 text-white"
                    : "bg-white/5 border border-white/10 text-white/80"
                }`}
              >
                <p className="whitespace-pre-wrap">{m.content}</p>
              </div>
            ))}
            {loadingChat && (
              <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-white/50 text-xs w-28 animate-pulse">
                Thinking...
              </div>
            )}
          </div>

          {/* Quick Query Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {suggestedQueries.slice(0, 3).map((sq, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(sq)}
                className="text-[10px] px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 hover:text-[#00F5A0] hover:border-[#00F5A0]/30 transition-all text-left"
              >
                💬 {sq}
              </button>
            ))}
          </div>

          {/* Chat input box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask Copilot a question about this feedback..."
              className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-white/25 focus:border-[#00F5A0] outline-none"
            />
            <button
              type="submit"
              disabled={loadingChat || !inputMessage.trim()}
              className="p-2 rounded-lg bg-[#00F5A0] text-black hover:brightness-110 disabled:opacity-40"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
