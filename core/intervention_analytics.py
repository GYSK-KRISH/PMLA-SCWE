"""Intervention Outcome Analytics & Effectiveness Engine for PMLA-SCWE.

Version 1.6 — Intervention Tracking & Outcome Intelligence
Features:
- Transparent multi-dimensional effectiveness calculation (0–100).
- Before vs. After Delta tracking (Risk score mitigation, Academic gains, Attendance recovery, LHS improvement).
- Outcome tier classification:
  - Highly Effective (>= 75)
  - Effective (50 - 74)
  - Moderate Improvement (25 - 49)
  - Needs Review / Escalated (< 25)
- Classroom cohort resolution rates and strategy rankings.
"""

from __future__ import annotations
from typing import Any
from datetime import datetime


TIER_HIGHLY_EFFECTIVE = "Highly Effective"
TIER_EFFECTIVE = "Effective"
TIER_MODERATE = "Moderate Improvement"
TIER_NEEDS_REVIEW = "Needs Review / Escalated"


def calculate_intervention_effectiveness(
    pre_metrics: dict[str, float | None],
    post_metrics: dict[str, float | None]
) -> dict[str, Any]:
    """Calculates transparent intervention outcome metrics and effectiveness rating.

    Formula:
      Delta_Risk (pts mitigated) = max(0, pre_risk - post_risk)
      Delta_Acad (% gain)       = max(0, post_acad - pre_acad)
      Delta_Att  (% gain)       = max(0, post_att - pre_att)
      Delta_LHS  (pts gain)     = max(0, post_lhs - pre_lhs)

      Effectiveness Score = (Delta_Risk * 0.35) + (Delta_Acad * 0.30) + (Delta_Att * 0.20) + (Delta_LHS * 0.15)
      Bounded within [0.0, 100.0]
    """
    pre_r = pre_metrics.get("risk_score") if pre_metrics.get("risk_score") is not None else 50.0
    post_r = post_metrics.get("risk_score") if post_metrics.get("risk_score") is not None else 50.0

    pre_acad = pre_metrics.get("academic_score") if pre_metrics.get("academic_score") is not None else 50.0
    post_acad = post_metrics.get("academic_score") if post_metrics.get("academic_score") is not None else 50.0

    pre_att = pre_metrics.get("attendance_rate") if pre_metrics.get("attendance_rate") is not None else 75.0
    post_att = post_metrics.get("attendance_rate") if post_metrics.get("attendance_rate") is not None else 75.0

    pre_lhs = pre_metrics.get("lhs_score") if pre_metrics.get("lhs_score") is not None else 60.0
    post_lhs = post_metrics.get("lhs_score") if post_metrics.get("lhs_score") is not None else 60.0

    # Calculate actual signed deltas
    delta_risk_raw = float(pre_r - post_r)          # Positive means risk was successfully reduced
    delta_acad_raw = float(post_acad - pre_acad)    # Positive means score improved
    delta_att_raw = float(post_att - pre_att)       # Positive means attendance improved
    delta_lhs_raw = float(post_lhs - pre_lhs)       # Positive means health score improved

    # Apply positive credit factors for effectiveness score
    gain_risk = max(0.0, delta_risk_raw)
    gain_acad = max(0.0, delta_acad_raw)
    gain_att = max(0.0, delta_att_raw)
    gain_lhs = max(0.0, delta_lhs_raw)

    score_raw = (gain_risk * 0.35) + (gain_acad * 0.30) + (gain_att * 0.20) + (gain_lhs * 0.15)
    # Scale score into 0-100 index (a 25-point recovery across dimensions is high impact)
    effectiveness_score = min(100.0, max(0.0, round(score_raw * 2.5, 1)))

    # Determine tier classification
    if effectiveness_score >= 75.0:
        tier = TIER_HIGHLY_EFFECTIVE
        narrative = "Significant positive recovery achieved across multiple dimensions. Targeted risk mitigated."
    elif effectiveness_score >= 50.0:
        tier = TIER_EFFECTIVE
        narrative = "Target milestones achieved with noticeable academic and behavioral improvements."
    elif effectiveness_score >= 25.0:
        tier = TIER_MODERATE
        narrative = "Moderate progress observed. Sustained monitoring and follow-up recommended."
    else:
        tier = TIER_NEEDS_REVIEW
        narrative = "Deficit persists. Case requires pedagogical review, parent consultation, or escalation."

    is_improved = (delta_risk_raw > 0 or delta_acad_raw > 0 or delta_att_raw > 0)

    return {
        "effectiveness_score": effectiveness_score,
        "effectiveness_tier": tier,
        "delta_risk": round(delta_risk_raw, 1),
        "delta_academic": round(delta_acad_raw, 1),
        "delta_attendance": round(delta_att_raw, 1),
        "delta_lhs": round(delta_lhs_raw, 1),
        "is_improved": is_improved,
        "narrative": narrative
    }


def aggregate_cohort_intervention_metrics(interventions: list[dict[str, Any]]) -> dict[str, Any]:
    """Computes classroom-wide intervention pipeline stats and resolution efficiency."""
    if not interventions:
        return {
            "total_interventions": 0,
            "active_count": 0,
            "completed_count": 0,
            "escalated_count": 0,
            "resolution_rate": 0.0,
            "avg_effectiveness": 0.0,
            "effective_count": 0,
            "needs_review_count": 0,
            "action_breakdown": {}
        }

    total = len(interventions)
    active = sum(1 for i in interventions if i.get("status") in ("PENDING", "IN_PROGRESS"))
    completed = sum(1 for i in interventions if i.get("status") == "COMPLETED")
    escalated = sum(1 for i in interventions if i.get("status") == "ESCALATED")

    completed_items = [i for i in interventions if i.get("status") == "COMPLETED" and i.get("effectiveness_score") is not None]
    effective_items = [i for i in completed_items if i.get("effectiveness_tier") in (TIER_HIGHLY_EFFECTIVE, TIER_EFFECTIVE)]

    resolution_rate = round((len(effective_items) / len(completed_items) * 100), 1) if completed_items else 0.0
    avg_eff = round(sum(float(i["effectiveness_score"]) for i in completed_items) / len(completed_items), 1) if completed_items else 0.0

    action_counts: dict[str, int] = {}
    for i in interventions:
        atype = i.get("action_type") or "Remedial Practice"
        action_counts[atype] = action_counts.get(atype, 0) + 1

    return {
        "total_interventions": total,
        "active_count": active,
        "completed_count": completed,
        "escalated_count": escalated,
        "resolution_rate": resolution_rate,
        "avg_effectiveness": avg_eff,
        "effective_count": len(effective_items),
        "needs_review_count": sum(1 for i in completed_items if i.get("effectiveness_tier") == TIER_NEEDS_REVIEW),
        "action_breakdown": action_counts
    }
