"""
Enterprise API Router — Phase 7.

Provides:
- POST /api/v1/enterprise/copilot/chat (Interactive Copilot Q&A for feedback and datasets)
- POST /api/v1/enterprise/benchmark (Side-by-side A/B brand and feedback comparison)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.main import enhanced_sentiment_analysis

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Intelligence v1"])


class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's query to the Copilot")
    analyzed_text: Optional[str] = Field(default="", description="The feedback or review text currently under analysis")
    sentiment: Optional[str] = Field(default="neutral", description="Current sentiment label")
    confidence: Optional[float] = Field(default=0.0, description="Current confidence score")
    triage: Optional[Dict[str, Any]] = Field(default=None, description="Current business triage payload")
    aspects: Optional[List[Dict[str, Any]]] = Field(default=None, description="Aspect breakdown")


class BenchmarkRequest(BaseModel):
    text_a: str = Field(..., min_length=3, max_length=2000, description="First text / brand feedback (Option A)")
    text_b: str = Field(..., min_length=3, max_length=2000, description="Second text / brand feedback (Option B)")
    label_a: Optional[str] = Field(default="Option A", description="Label for Option A")
    label_b: Optional[str] = Field(default="Option B", description="Label for Option B")


@router.post(
    "/copilot/chat",
    summary="Interactive AI Copilot Q&A",
    description="Provides real-time conversational intelligence, answer extraction, and email draft revisions on analyzed feedback.",
)
def copilot_chat(data: CopilotChatRequest):
    q = data.message.lower().strip()
    sentiment = data.sentiment or "neutral"
    triage = data.triage or {}
    aspects = data.aspects or []
    text = data.analyzed_text or ""

    urgency = triage.get("urgency", "Standard")
    intent = triage.get("intent", "General Feedback")
    action = triage.get("recommended_action", "No immediate escalation required.")
    aspect_names = [a.get("label", "") for a in aspects]
    aspect_str = ", ".join(aspect_names) if aspect_names else "overall customer experience"

    if any(k in q for k in ["draft", "reply", "email", "respond", "apologize", "write"]):
        reply = (
            f"Here is a customized customer response tailored to this feedback:\n\n"
            f"\"Dear Valued Customer,\n\n"
            f"Thank you for sharing your thoughts regarding our {aspect_str}. "
            f"We take feedback like this very seriously. Our team is actively reviewing your notes "
            f"to ensure your concerns are resolved swiftly and completely.\n\n"
            f"Please reach out directly to support@sentiai.com if we can provide any immediate support.\n\n"
            f"Warm regards,\nThe Customer Experience Team\""
        )
    elif any(k in q for k in ["action", "what should we do", "next step", "recommend", "triage"]):
        reply = (
            f"**Operational Recommendation (Urgency: {urgency})**:\n\n"
            f"- **Immediate Action:** {action}\n"
            f"- **Primary Intent:** {intent}\n"
            f"- **Focus Areas:** {aspect_str}\n"
            f"- **Risk Assessment:** {triage.get('churn_risk', 'Low')} churn likelihood."
        )
    elif any(k in q for k in ["why", "reason", "cause", "explain"]):
        reply = (
            f"The model classified this feedback as **{sentiment.upper()}** ({data.confidence:.1%} confidence) "
            f"primarily because the commentary impacts **{aspect_str}**. "
            f"Key intent recognized: *{intent}*."
        )
    elif any(k in q for k in ["aspect", "topic", "breakdown", "category"]):
        if aspects:
            aspect_lines = "\n".join([f"- **{a.get('label')}:** {a.get('polarity').title()} (Score: {a.get('score', 0):+.2f})" for a in aspects])
            reply = f"Here is the breakdown by business aspect:\n\n{aspect_lines}"
        else:
            reply = "No distinct department aspects were triggered; the feedback represents global sentiment."
    else:
        reply = (
            f"I have reviewed the feedback. The customer's tone is **{sentiment}** ({data.confidence:.1%} confidence). "
            f"The primary concern touches on **{aspect_str}**. "
            f"Recommended next step: *{action}*. "
            f"You can ask me to draft a reply email, summarize top drivers, or evaluate churn risk!"
        )

    return {
        "reply": reply,
        "sentiment": sentiment,
        "urgency": urgency,
    }


@router.post(
    "/benchmark",
    summary="A/B Brand & Product Sentiment Comparison",
    description="Evaluates two pieces of feedback or brand texts and computes win/loss score differentials.",
)
def benchmark_comparison(data: BenchmarkRequest):
    res_a = enhanced_sentiment_analysis(data.text_a)
    res_b = enhanced_sentiment_analysis(data.text_b)

    score_map = {"positive": 1.0, "neutral": 0.0, "uncertain": 0.0, "negative": -1.0}
    val_a = score_map.get(res_a["sentiment"], 0.0) * res_a["confidence"]
    val_b = score_map.get(res_b["sentiment"], 0.0) * res_b["confidence"]

    diff = round(val_a - val_b, 4)
    if diff > 0.05:
        winner = data.label_a
        verdict = f"{data.label_a} leads with a net sentiment advantage of {abs(diff):.2f} pts."
    elif diff < -0.05:
        winner = data.label_b
        verdict = f"{data.label_b} leads with a net sentiment advantage of {abs(diff):.2f} pts."
    else:
        winner = "Tie"
        verdict = "Both options exhibit comparable sentiment distribution."

    return {
        "option_a": {
            "label": data.label_a,
            "text": data.text_a,
            "sentiment": res_a["sentiment"],
            "confidence": res_a["confidence"],
            "probabilities": res_a["probabilities"],
            "triage": res_a.get("triage"),
            "aspects": res_a.get("aspects"),
        },
        "option_b": {
            "label": data.label_b,
            "text": data.text_b,
            "sentiment": res_b["sentiment"],
            "confidence": res_b["confidence"],
            "probabilities": res_b["probabilities"],
            "triage": res_b.get("triage"),
            "aspects": res_b.get("aspects"),
        },
        "winner": winner,
        "delta": diff,
        "verdict": verdict,
    }
