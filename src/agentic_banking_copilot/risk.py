"""Transparent, rule-based AML / onboarding risk scoring.

This is a demo rules layer, not a production AML model. Every point is
explained in the output so a reviewer can see *why* a case escalated —
the same explainability idea as SHAP-style reporting in the author's
production work, without claiming this demo is that system.
"""

from __future__ import annotations

HIGH_RISK_COUNTRIES = {"country-x", "country-y", "high-risk-jurisdiction"}

REQUIRED_DOCUMENTS = ["government_id", "proof_of_address"]


def score_risk(
    *,
    country: str = "",
    is_pep: bool = False,
    is_sanctions_match: bool = False,
    initial_deposit_usd: float = 0.0,
    expected_monthly_volume_usd: float = 0.0,
    documents_provided: list[str] | None = None,
) -> dict:
    """Return a risk score (0-100), level, and human-readable reasons."""
    provided = set(documents_provided or [])
    score = 10  # baseline: every new account carries some review risk
    reasons = ["Baseline onboarding risk: +10"]

    if is_sanctions_match:
        score += 60
        reasons.append("Sanctions-list name match: +60")
    if is_pep:
        score += 30
        reasons.append("Politically exposed person (PEP): +30")
    if country.lower() in HIGH_RISK_COUNTRIES:
        score += 40
        reasons.append(f"High-risk jurisdiction ({country}): +40")
    if initial_deposit_usd >= 50_000:
        score += 20
        reasons.append("Initial deposit >= $50,000: +20")
    if expected_monthly_volume_usd >= 100_000:
        score += 15
        reasons.append("Expected monthly volume >= $100,000: +15")

    missing = [d for d in REQUIRED_DOCUMENTS if d not in provided]
    if missing:
        score += 10
        reasons.append(f"Incomplete documents ({', '.join(missing)}): +10")

    score = min(score, 100)
    level = "high" if score >= 70 else "medium" if score >= 40 else "low"
    return {"score": score, "level": level, "reasons": reasons, "missing_documents": missing}
