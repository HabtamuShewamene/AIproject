"""
Enterprise Aspect-Based Sentiment Analysis (ABSA) & Business Triage Service.

Provides:
- Multi-dimensional aspect extraction (Product, Support, Billing, Performance, Logistics)
- Churn risk assessment & urgency grading (Normal, Attention, Critical, Escalation)
- Intent classification (Bug Report, Feature Request, Billing Issue, Churn Threat, Praise)
- Actionable operational recommendations for executive and support teams.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enterprise Aspect Lexicons
# ---------------------------------------------------------------------------

ASPECT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "product_features": {
        "label": "Product & Capabilities",
        "icon": "Package",
        "keywords": [
            "feature", "features", "tool", "function", "functionality", "quality",
            "update", "version", "capability", "settings", "option", "button",
            "integration", "api", "model", "accuracy", "algorithm", "output",
        ],
    },
    "customer_support": {
        "label": "Customer Support",
        "icon": "Headphones",
        "keywords": [
            "support", "service", "agent", "representative", "helpdesk", "ticket",
            "reply", "response", "replied", "waited", "waiting", "helped",
            "rude", "friendly", "empathy", "resolved", "unhelpful", "email",
        ],
    },
    "billing_pricing": {
        "label": "Pricing & Billing",
        "icon": "CreditCard",
        "keywords": [
            "price", "pricing", "cost", "expensive", "cheap", "charge", "charged",
            "bill", "billing", "subscription", "plan", "fee", "fees", "refund",
            "receipt", "invoice", "overpriced", "worth", "money", "dollar", "card",
        ],
    },
    "performance_ux": {
        "label": "Performance & UX",
        "icon": "Zap",
        "keywords": [
            "slow", "fast", "speed", "lag", "latency", "crash", "crashed", "bug",
            "error", "freeze", "down", "outage", "glitch", "ui", "ux", "design",
            "interface", "mobile", "desktop", "load", "loading", "blazing", "smooth",
        ],
    },
    "fulfillment_logistics": {
        "label": "Fulfillment & Delivery",
        "icon": "Truck",
        "keywords": [
            "shipping", "ship", "delivery", "delivered", "package", "transit",
            "arrived", "delay", "delayed", "late", "tracking", "lost", "damaged",
            "courier", "order", "status",
        ],
    },
}

CHURN_INTENT_PATTERNS = [
    r"\b(cancel|canceling|cancelling|unsubscrib|switch|switching to|leaving|delete my account|going to competitor)\b",
    r"\b(waste of money|rip off|ripoff|never using again|worst service|lawsuit|attorney|report you)\b",
    r"\b(done with this|switching to rival|goodbye|unacceptable)\b",
]

BUG_PATTERNS = [
    r"\b(bug|bugs|error|errors|crash|crashed|crashes|crashing|broken|fail|fails|failed|failing|exception|freeze|freezes|froze|freezing|stuck|glitch|glitches|regression)\b",
]

FEATURE_REQUEST_PATTERNS = [
    r"\b(please add|would love|wish there was|feature request|could you add|need a way to|suggestion)\b",
]

BILLING_PATTERNS = [
    r"\b(charged twice|overcharged|refund|unauthorized charge|billing error|cancel subscription)\b",
]


# ---------------------------------------------------------------------------
# Aspect Extraction Logic
# ---------------------------------------------------------------------------

def extract_aspects(text: str, base_sentiment: str, confidence: float) -> List[Dict[str, Any]]:
    """
    Extract business aspects present in text and evaluate their localized polarity.
    """
    lower = text.lower()
    sentences = re.split(r"[.!?\n]+", text)
    aspect_results: List[Dict[str, Any]] = []

    pos_cues = {"great", "good", "love", "amazing", "smooth", "fast", "excellent", "superb", "helpful", "delighted"}
    neg_cues = {"bad", "slow", "terrible", "awful", "horrible", "broken", "delayed", "rude", "expensive", "poor", "unacceptable", "bug", "error"}

    for key, spec in ASPECT_DEFINITIONS.items():
        matched_words = [w for w in spec["keywords"] if re.search(rf"\b{re.escape(w)}\b", lower)]
        if not matched_words:
            continue

        # Score local sentiment in sentences containing the aspect keywords
        aspect_pos = 0
        aspect_neg = 0
        for sent in sentences:
            s_lower = sent.lower()
            if any(w in s_lower for w in matched_words):
                aspect_pos += sum(1 for w in pos_cues if w in s_lower)
                aspect_neg += sum(1 for w in neg_cues if w in s_lower)

        # Fallback to base sentiment if no explicit sentiment words in the aspect sentence
        if aspect_pos > aspect_neg:
            polarity = "positive"
            score = 0.85
        elif aspect_neg > aspect_pos:
            polarity = "negative"
            score = -0.85
        else:
            if base_sentiment == "positive":
                polarity = "positive"
                score = round(confidence, 2)
            elif base_sentiment == "negative":
                polarity = "negative"
                score = round(-confidence, 2)
            else:
                polarity = "neutral"
                score = 0.0

        aspect_results.append({
            "aspect_id": key,
            "label": spec["label"],
            "icon": spec["icon"],
            "polarity": polarity,
            "score": score,
            "matched_keywords": matched_words[:4],
        })

    return aspect_results


# ---------------------------------------------------------------------------
# Business Triage & Urgency Evaluation
# ---------------------------------------------------------------------------

def evaluate_business_triage(text: str, sentiment: str, confidence: float) -> Dict[str, Any]:
    """
    Evaluate operational urgency, churn risk, intent category, and recommended resolution action.
    """
    lower = text.lower()

    # Detect Churn Threat
    is_churn_threat = any(re.search(pat, lower, re.I) for pat in CHURN_INTENT_PATTERNS)
    is_bug = any(re.search(pat, lower, re.I) for pat in BUG_PATTERNS)
    is_feature_req = any(re.search(pat, lower, re.I) for pat in FEATURE_REQUEST_PATTERNS)
    is_billing_issue = any(re.search(pat, lower, re.I) for pat in BILLING_PATTERNS)

    # Urgency & Churn Risk Tier
    if is_churn_threat and sentiment == "negative":
        urgency = "Critical"
        urgency_level = 4
        churn_risk = "High"
        intent = "Customer Churn Risk"
        recommended_action = "Trigger immediate VIP customer retention outreach and assign a senior customer success manager."
    elif is_billing_issue and sentiment == "negative":
        urgency = "High"
        urgency_level = 3
        churn_risk = "Medium"
        intent = "Billing & Refund Dispute"
        recommended_action = "Route to Billing Department with priority expedite flag for refund review."
    elif is_bug and sentiment == "negative":
        urgency = "Medium"
        urgency_level = 2
        churn_risk = "Low"
        intent = "Product Defect / Bug Report"
        recommended_action = "File ticket in Engineering backlog and link user contact to incident report."
    elif is_feature_req:
        urgency = "Low"
        urgency_level = 1
        churn_risk = "None"
        intent = "Product Feature Request"
        recommended_action = "Log user insight in Product Management roadmapping portal for triage."
    elif sentiment == "positive" and confidence >= 0.85:
        urgency = "Low"
        urgency_level = 0
        churn_risk = "None"
        intent = "Brand Advocacy & Praise"
        recommended_action = "Share review with Marketing for social proof highlight or case study quote."
    elif sentiment == "negative":
        urgency = "Attention"
        urgency_level = 2
        churn_risk = "Medium"
        intent = "General Dissatisfaction"
        recommended_action = "Send standard empathetic customer support reply within standard SLA."
    else:
        urgency = "Standard"
        urgency_level = 1
        churn_risk = "None"
        intent = "Informational / Neutral Feedback"
        recommended_action = "No immediate operational escalation required; archive in sentiment analytics."

    # Executive Takeaway 1-liner
    if sentiment == "positive":
        takeaway = f"Customer expressed strong satisfaction (confidence {confidence:.0%}) with high brand affinity."
    elif urgency == "Critical":
        takeaway = "Active churn risk detected: customer expresses intent to leave or discontinue service."
    elif sentiment == "negative":
        takeaway = f"Negative feedback detected ({intent}) requiring prompt customer engagement to de-escalate."
    else:
        takeaway = "Balanced or neutral feedback with low risk of customer attrition."

    return {
        "urgency": urgency,
        "urgency_level": urgency_level,
        "churn_risk": churn_risk,
        "intent": intent,
        "recommended_action": recommended_action,
        "executive_takeaway": takeaway,
    }
