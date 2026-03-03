from typing import Any, Dict, List


def run_pipeline(text: str, locale: str = "en") -> Dict[str, Any]:
    """
    Simple hybrid-style moderation pipeline (rules + scoring).
    Streamlit-friendly (returns plain dicts).
    """
    findings: List[Dict[str, Any]] = []
    warnings: List[str] = []

    t = (text or "").lower().strip()

    # -----------------------------
    # Scam / fraud signals (rules)
    # -----------------------------
    scam_score = 0.0
    scam_reasons: List[str] = []
    if "gift card" in t or "steam card" in t or "itunes card" in t:
        scam_score = max(scam_score, 0.75)
        scam_reasons.append("gift_card_payment")
    if "verify your account" in t or "account will be closed" in t or "account closed" in t:
        scam_score = max(scam_score, 0.60)
        scam_reasons.append("account_threat_or_impersonation")
    if "urgent" in t or "act now" in t or "limited time" in t:
        scam_score = max(scam_score, 0.40)
        scam_reasons.append("urgency_pressure")

    if scam_score > 0:
        findings.append(
            {"category": "scam_fraud", "severity": scam_score, "reasons": scam_reasons}
        )
        warnings.append("Possible scam/fraud — avoid payments, suspicious links, or sharing personal info.")

    # -----------------------------------
    # Sexual content / solicitation (rules)
    # -----------------------------------
    sex_score = 0.0
    sex_reasons: List[str] = []
    sexual_phrases = ["send nudes", "dm for nudes", "hook up", "hookup", "sex now"]
    if any(p in t for p in sexual_phrases):
        sex_score = max(sex_score, 0.70)
        sex_reasons.append("explicit_or_solicitation_phrase")

    if sex_score > 0:
        findings.append(
            {"category": "sexual_content", "severity": sex_score, "reasons": sex_reasons}
        )
        warnings.append("Sexual content — may include explicit or suggestive language.")

    # -----------------------------
    # Child safety risk (rules)
    # -----------------------------
    child_score = 0.0
    child_reasons: List[str] = []
    minor_markers = ["i'm 16", "i am 16", "i'm 17", "i am 17", "under 18", "minor"]
    if any(m in t for m in minor_markers):
        child_score = max(child_score, 0.85)
        child_reasons.append("minor_mentioned")
    if "older men" in t or "older women" in t or "age gap" in t:
        child_score = max(child_score, 0.60)
        child_reasons.append("adult_minor_context")

    if child_score > 0:
        findings.append(
            {"category": "child_safety", "severity": child_score, "reasons": child_reasons}
        )
        warnings.append("Child safety risk — may involve minors, grooming, or exploitation.")

    # -----------------------------
    # Overall decision
    # -----------------------------
    overall = max([f["severity"] for f in findings], default=0.0)

    # Block if very high severity OR child-safety is high
    safe_to_show = True
    if overall >= 0.70:
        safe_to_show = False
    if any(f["category"] == "child_safety" and f["severity"] >= 0.60 for f in findings):
        safe_to_show = False

    return {
        "safe_to_show": safe_to_show,
        "overall_severity": float(overall),
        "trigger_warnings": warnings,
        "findings": findings,
        "debug": {"locale": locale},
    }
