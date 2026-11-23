"""Accessibility router — Phase 6: WCAG 2.1 AA compliance report endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.accessibility import get_a11y_report, build_aria_metadata

router = APIRouter(prefix="/api/v1/accessibility", tags=["Accessibility"])


@router.get(
    "/report",
    summary="WCAG 2.1 AA compliance report",
    description=(
        "Returns the platform's accessibility compliance checklist against WCAG 2.1 AA criteria. "
        "Useful for audit tooling, CI gates, and automated accessibility regression testing."
    ),
)
def accessibility_report():
    return get_a11y_report()


@router.get(
    "/aria-labels",
    summary="ARIA label reference for all sentiment states",
    description=(
        "Returns the canonical ARIA label strings used by the frontend for all sentiment values "
        "and confidence tiers, enabling frontend/backend contract consistency."
    ),
)
def aria_labels():
    """Return reference ARIA labels for all valid sentiment × confidence combinations."""
    sentiments = ["positive", "negative", "neutral", "uncertain"]
    examples = []
    for sentiment in sentiments:
        for low_confidence, confidence in [(False, 0.92), (False, 0.74), (False, 0.55), (True, 0.38)]:
            meta = build_aria_metadata(
                sentiment=sentiment,
                confidence=confidence,
                low_confidence=low_confidence,
                language="en",
            )
            examples.append({
                "sentiment": sentiment,
                "confidence": confidence,
                "low_confidence": low_confidence,
                "aria": meta,
            })
    return {"aria_reference": examples}
