from typing import Any, Dict, List


def run_pipeline(text: str, locale: str = "en") -> Dict[str, Any]:
    """
    Streamlit-friendly moderation pipeline (rules + scoring).
    Returns plain dicts and uses safe .get() access everywhere.
    """
    findings: List[Dict[str, Any]] = []
    warnings: List[str] = []

    t = (text or "").lower().strip()

    # -----------------------------
    # Scam / fraud signals
    # -----------------------------
    scam_score = 0.0
    scam_reasons: List[str] = []
    if any(x in t for x in ["gift card", "steam card", "itunes card"]):
        scam_score = max(scam_score, 0.80)
        scam_reasons.append("gift_card_payment")
    if any(x in t for x in ["verify your account", "account will be closed", "account closed"]):
        scam_score = max(scam_score, 0.65)
        scam_reasons.append("account_threat_or_impersonation")
    if any(x in t for x in ["urgent", "act now", "limited time", "final notice"]):
        scam_score = max(scam_score, 0.40)
        scam_reasons.append("urgency_pressure")
    if any(x in t for x in ["crypto", "bitcoin", "wallet address"]):
        scam_score = max(scam_score, 0.55)
        scam_reasons.append("crypto_payment_request")

    if scam_score > 0:
        findings.append(
            {"category": "scam_fraud", "severity": float(scam_score), "reasons": scam_reasons}
        )
        warnings.append("Possible scam/fraud — avoid payments, suspicious links, or sharing personal info.")

    # -----------------------------
    # Sexual content / solicitation
    # -----------------------------
    sex_score = 0.0
    sex_reasons: List[str] = []
    sexual_phrases = [
        "send nudes", "dm for nudes", "private pics", "exclusive content",
        "hook up", "hookup", "sex now"
    ]
    if any(p in t for p in sexual_phrases):
        sex_score = max(sex_score, 0.70)
        sex_reasons.append("explicit_or_solicitation_phrase")

    if sex_score > 0:
        findings.append(
            {"category": "sexual_content", "severity": float(sex_score), "reasons": sex_reasons}
        )
        warnings.append("Sexual content — may include explicit or suggestive language.")

    # -----------------------------
    # Child safety risk
    # -----------------------------
    child_score = 0.0
    child_reasons: List[str] = []
    minor_markers = ["i'm 16", "i am 16", "i'm 17", "i am 17", "under 18", "minor"]
    if any(m in t for m in minor_markers):
        child_score = max(child_score, 0.85)
        child_reasons.append("minor_mentioned")
    if any(x in t for x in ["older men", "older women", "age gap", "meet privately"]):
        child_score = max(child_score, 0.60)
        child_reasons.append("adult_minor_context")

    if child_score > 0:
        findings.append(
            {"category": "child_safety", "severity": float(child_score), "reasons": child_reasons}
        )
        warnings.append("Child safety risk — may involve minors, grooming, or exploitation.")

    # -----------------------------
    # Overall severity (SAFE)
    # -----------------------------
    overall = max([float(f.get("severity", 0.0)) for f in findings], default=0.0)

    # -----------------------------
    # Decision (SAFE)
    # -----------------------------
    safe_to_show = True
    if overall >= 0.70:
        safe_to_show = False

    # block child safety if high
    if any(
        f.get("category") == "child_safety" and float(f.get("severity", 0.0)) >= 0.60
        for f in findings
    ):
        safe_to_show = False

    return {
        "safe_to_show": bool(safe_to_show),
        "overall_severity": float(overall),
        "trigger_warnings": warnings,
        "findings": findings,
        "debug": {"locale": locale, "text_len": len(text or "")},
    }
