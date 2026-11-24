"""
Enterprise AI Copilot & Automated Resolution Drafter Service.

Provides:
- 3 key bullet-point drivers synthesized from neural sentiment & triage
- Ready-to-send customer response drafts (Empathetic, Solution-Oriented, Appreciation)
- Executive quick-briefs for internal handoff
- Recommended interactive drill-down queries for the user.
"""

from __future__ import annotations

from typing import Any, Dict, List


def generate_copilot_assistance(
    text: str,
    sentiment: str,
    confidence: float,
    triage: Dict[str, Any],
    aspects: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate actionable AI assistant insights and customer response drafts.
    """
    urgency = triage.get("urgency", "Standard")
    intent = triage.get("intent", "General")
    aspect_labels = [a["label"] for a in aspects]
    aspects_str = ", ".join(aspect_labels) if aspect_labels else "general service"

    # Key analytical takeaways
    key_drivers: List[str] = []
    if sentiment == "positive":
        key_drivers.append(f"Strong customer loyalty signals detected around {aspects_str}.")
        key_drivers.append(f"Confidence score of {confidence:.1%} indicates unambiguous brand affinity.")
        key_drivers.append("Opportunity to convert customer into a brand advocate or review referral.")
    elif sentiment == "negative":
        key_drivers.append(f"Dissatisfaction primarily concentrated on {aspects_str}.")
        key_drivers.append(f"Classified under intent category '{intent}' with urgency level '{urgency}'.")
        if triage.get("churn_risk") in {"High", "Medium"}:
            key_drivers.append("High risk of customer attrition or negative word-of-mouth if unaddressed.")
        else:
            key_drivers.append("Standard resolution path feasible through prompt acknowledgment.")
    else:
        key_drivers.append(f"Balanced or ambivalent commentary regarding {aspects_str}.")
        key_drivers.append("No acute operational failure detected, but monitors should track recurring themes.")
        key_drivers.append("Customer may be persuaded towards positive sentiment with proactive support.")

    # Response Drafts
    if sentiment == "negative":
        draft_empathetic = (
            f"Dear customer,\n\n"
            f"Thank you for sharing your honest feedback regarding our {aspects_str}. "
            f"We are truly sorry to hear that your experience fell short of expectations. "
            f"We understand how frustrating this is, and our leadership team is actively reviewing your comments "
            f"so we can resolve this matter for you immediately.\n\n"
            f"Please reach out directly to us at support@sentiai.internal with your account details "
            f"so a dedicated specialist can assist you right away."
        )
        draft_solution = (
            f"Hello,\n\n"
            f"We have flagged your feedback regarding {aspects_str} for immediate investigation. "
            f"Our engineering and support teams are currently reviewing this issue to ensure a swift fix. "
            f"To expedite your resolution, our priority queue has been notified.\n\n"
            f"Thank you for your patience as we make this right."
        )
        draft_executive = (
            f"Executive Summary: Customer expresses urgent dissatisfaction ({intent}, Urgency: {urgency}) "
            f"centered on {aspects_str}. Immediate retention intervention recommended."
        )
    elif sentiment == "positive":
        draft_empathetic = (
            f"Hello!\n\n"
            f"Thank you so much for the wonderful feedback regarding our {aspects_str}! "
            f"Our team puts tremendous care into delivering an exceptional experience, and knowing "
            f"that it resonated with you made our day.\n\n"
            f"Thank you for being a valued part of our community!"
        )
        draft_solution = (
            f"Hi there,\n\n"
            f"We appreciate your positive review on our {aspects_str}. "
            f"We are constantly rolling out new enhancements, and your support motivates us to keep raising the bar.\n\n"
            f"If you ever have ideas or feature requests, we would love to hear them!"
        )
        draft_executive = (
            f"Executive Summary: Strong positive sentiment validated ({confidence:.1%} confidence). "
            f"Highlights strengths in {aspects_str}. Candidate for marketing testimonial."
        )
    else:
        draft_empathetic = (
            f"Hello,\n\n"
            f"Thank you for taking the time to share your thoughts on our {aspects_str}. "
            f"We appreciate your balanced perspective and are always striving to improve our services.\n\n"
            f"Please feel free to reply with any specific suggestions you may have!"
        )
        draft_solution = (
            f"Hi,\n\n"
            f"Thanks for your feedback. We have noted your comments regarding {aspects_str} in our "
            f"continuous improvement backlog.\n\n"
            f"Let us know if you need any assistance."
        )
        draft_executive = (
            f"Executive Summary: Neutral / mixed feedback logged for {aspects_str}. "
            f"Sentiment is stable with no immediate churn risk."
        )

    suggested_queries = [
        f"What are the top complaints regarding {aspects_str}?",
        "How does this compare to our benchmark average?",
        "What specific words triggered this sentiment classification?",
        "Draft a follow-up inquiry asking for more technical details.",
    ]

    return {
        "key_drivers": key_drivers,
        "suggested_queries": suggested_queries,
        "drafts": {
            "empathetic": draft_empathetic,
            "solution_oriented": draft_solution,
            "executive_brief": draft_executive,
        },
    }
