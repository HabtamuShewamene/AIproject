"""Conversation intelligence orchestrator (Blueprint Modules 2, 4, 5, 6).

Coordinates post + reply thread retrieval, multi-stage AI sentiment analysis,
engagement weighting, topic clustering, and evidence-grounded recommendations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.providers.base import ConversationDataset, ReplyData
from app.providers.factory import get_social_provider
from app.topic_clustering import cluster_topics


def _sentiment_to_numeric(sentiment: str) -> float:
    if sentiment == "positive":
        return 1.0
    if sentiment == "negative":
        return -1.0
    return 0.0


def analyze_conversation_thread(
    url: str,
    max_replies: int = 50,
    include_nested: bool = True,
    provider_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full end-to-end Twitter/X conversation thread intelligence pipeline.
    """
    from app.main import enhanced_sentiment_analysis
    provider = get_social_provider(provider_name)
    dataset: Optional[ConversationDataset] = provider.fetch_conversation(
        url=url,
        max_replies=max_replies,
        include_nested=include_nested,
    )

    if not dataset:
        return {
            "status": "error",
            "error": f"Failed to retrieve conversation thread using provider '{provider.provider_name}'. Post may be private or deleted.",
            "data": None,
        }

    original = dataset.original_post
    replies = dataset.replies
    prov = dataset.provenance

    # 1. Analyze Root Post
    root_sentiment = enhanced_sentiment_analysis(original.text)

    # 2. Analyze Every Reply Individually
    analyzed_replies = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    total_engagement_weight = 0.0
    weighted_sentiment_sum = 0.0

    complaint_cues = ["broken", "crash", "bug", "terrible", "unusable", "poor", "freeze", "disappoint", "worst", "fail"]
    praise_cues = ["great", "love", "awesome", "excellent", "fast", "best", "super", "clean", "smooth", "kudos"]

    frequently_repeated_complaints = []
    frequently_repeated_praise = []

    for r in replies:
        analysis = enhanced_sentiment_analysis(r.text)
        sentiment = analysis.get("sentiment", "neutral")
        confidence = analysis.get("confidence", 0.0)

        if sentiment == "positive":
            positive_count += 1
        elif sentiment == "negative":
            negative_count += 1
        else:
            neutral_count += 1

        # Weight by engagement (likes + retweets*2 + 1 base)
        weight = float(r.metrics.likes + (r.metrics.retweets * 2) + 1)
        total_engagement_weight += weight
        weighted_sentiment_sum += (_sentiment_to_numeric(sentiment) * weight)

        # Categorize customer feedback signals
        text_lower = r.text.lower()
        if any(c in text_lower for c in complaint_cues):
            frequently_repeated_complaints.append({
                "reply_id": r.reply_id,
                "author": r.author_username,
                "text": r.text,
                "likes": r.metrics.likes,
            })
        if any(p in text_lower for p in praise_cues):
            frequently_repeated_praise.append({
                "reply_id": r.reply_id,
                "author": r.author_username,
                "text": r.text,
                "likes": r.metrics.likes,
            })

        analyzed_replies.append({
            "reply_id": r.reply_id,
            "parent_id": r.parent_id,
            "author": r.author_username,
            "text": r.text,
            "sentiment": sentiment,
            "confidence": confidence,
            "aspects": analysis.get("aspects", []),
            "triage": analysis.get("triage", {}),
            "metrics": {
                "likes": r.metrics.likes,
                "retweets": r.metrics.retweets,
                "replies": r.metrics.replies,
            },
            "is_nested": r.is_nested,
            "depth": r.depth,
        })

    # 3. Public Opinion Analytics (Blueprint Module 4)
    total_analyzed = len(analyzed_replies)
    if total_analyzed > 0:
        positive_pct = round((positive_count / total_analyzed) * 100, 2)
        negative_pct = round((negative_count / total_analyzed) * 100, 2)
        neutral_pct = round((neutral_count / total_analyzed) * 100, 2)
        weighted_score = round(weighted_sentiment_sum / total_engagement_weight, 3) if total_engagement_weight > 0 else 0.0
    else:
        positive_pct = 0.0
        negative_pct = 0.0
        neutral_pct = 0.0
        weighted_score = 0.0

    # Determine overall public stance
    if positive_pct >= 55.0:
        overall_stance = "Predominantly Positive"
    elif negative_pct >= 45.0:
        overall_stance = "Predominantly Negative"
    elif abs(positive_pct - negative_pct) <= 15.0 and (positive_pct + negative_pct) > 50.0:
        overall_stance = "Polarized / Divided"
    else:
        overall_stance = "Neutral / Mixed"

    # 4. Topic Extraction from replies (Blueprint Module 5)
    cluster_res = cluster_topics(analyzed_replies) if analyzed_replies else {}
    extracted_topics = cluster_res.get("clusters", []) if isinstance(cluster_res, dict) else []

    # 5. Grounded AI Recommendations (Blueprint Module 6)
    recommendations = _generate_grounded_recommendations(
        overall_stance=overall_stance,
        negative_pct=negative_pct,
        positive_pct=positive_pct,
        complaints=frequently_repeated_complaints,
        praise=frequently_repeated_praise,
        topics=extracted_topics,
    )

    return {
        "status": "ok",
        "error": None,
        "data": {
            "root_post": {
                "post_id": original.post_id,
                "url": original.url,
                "text": original.text,
                "author": original.author_username,
                "author_name": original.author_name,
                "verified": original.author_verified,
                "created_at": original.created_at,
                "metrics": {
                    "likes": original.metrics.likes,
                    "retweets": original.metrics.retweets,
                    "replies": original.metrics.replies,
                    "quotes": original.metrics.quotes,
                    "views": original.metrics.views,
                },
                "sentiment": root_sentiment.get("sentiment"),
                "confidence": root_sentiment.get("confidence"),
                "aspects": root_sentiment.get("aspects", []),
                "triage": root_sentiment.get("triage", {}),
            },
            "public_opinion": {
                "overall_stance": overall_stance,
                "total_analyzed_comments": total_analyzed,
                "distribution": {
                    "positive_percentage": positive_pct,
                    "negative_percentage": negative_pct,
                    "neutral_percentage": neutral_pct,
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "neutral_count": neutral_count,
                },
                "engagement_weighted_sentiment_score": weighted_score,
                "weighted_interpretation": (
                    "Net Positive Audience Reception"
                    if weighted_score > 0.15
                    else "Net Negative Audience Resistance"
                    if weighted_score < -0.15
                    else "Balanced Public Reaction"
                ),
            },
            "topic_intelligence": {
                "topics": extracted_topics[:5],
                "top_complaints": frequently_repeated_complaints[:5],
                "top_praise": frequently_repeated_praise[:5],
            },
            "executive_recommendations": recommendations,
            "replies": analyzed_replies,
            "provenance": {
                "source_url": prov.source_url,
                "provider_name": prov.provider_name,
                "collected_at": prov.collected_at,
                "total_replies_on_x": prov.total_replies_on_x,
                "replies_collected": prov.replies_collected,
                "coverage_percentage": prov.coverage_percentage,
                "is_complete": prov.is_complete,
                "collection_method": prov.collection_method,
                "access_limitations": prov.access_limitations,
            },
        },
    }


def _generate_grounded_recommendations(
    overall_stance: str,
    negative_pct: float,
    positive_pct: float,
    complaints: List[dict],
    praise: List[dict],
    topics: List[dict],
) -> List[dict]:
    """Generate strictly grounded recommendations referencing real comment evidence."""
    recs = []

    if negative_pct >= 35.0 or len(complaints) > 0:
        top_complaint = complaints[0]["text"] if complaints else "Multiple critical responses identified"
        recs.append({
            "priority": "Critical" if negative_pct >= 50.0 else "High",
            "focus_area": "Customer Sentiment Mitigation",
            "finding": f"High volume of dissatisfaction ({negative_pct}% negative comments) detected in public replies.",
            "recommended_action": "Publish an official clarification or fix notice addressing the top community grievance.",
            "evidence_quote": top_complaint,
            "supporting_comments_count": len(complaints),
        })

    if positive_pct >= 40.0 and len(praise) > 0:
        top_praise = praise[0]["text"]
        recs.append({
            "priority": "Medium",
            "focus_area": "Product Advocacy & Amplification",
            "finding": f"Strong positive reception ({positive_pct}%) around product aesthetics and performance.",
            "recommended_action": "Engage and repost top advocates to amplify social momentum.",
            "evidence_quote": top_praise,
            "supporting_comments_count": len(praise),
        })

    if not recs:
        recs.append({
            "priority": "Standard",
            "focus_area": "Ongoing Audience Monitoring",
            "finding": "Audience response is currently balanced without urgent crisis triggers.",
            "recommended_action": "Continue tracking comment sentiment over the next 24-48 hours.",
            "evidence_quote": "Feedback remains distributed evenly across positive and neutral sentiment.",
            "supporting_comments_count": 0,
        })

    return recs
