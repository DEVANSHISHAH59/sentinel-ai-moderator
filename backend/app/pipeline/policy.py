from typing import Any, Dict, List


def run_pipeline(text: str, locale: str = "en") -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    warnings: List[str] = []

    t = (text or "").lower().strip()

    # -----------------------------
    # Scam / fraud
    # -----------------------------
    scam_score = 0.0
    scam_reasons = []

    if any(x in t for x in ["gift card", "steam card", "itunes card"]):
        scam_score = max(scam_score, 0.80)
        scam_reasons.append("gift_card_payment")

    if any(x in t for x in ["verify your account", "account will be closed", "account closed"]):
        scam_score = max(scam_score, 0.65)
        scam_reasons.append("account_threat")

    if any(x in t for x in ["urgent", "act now", "final notice"]):
        scam_score = max(scam_score, 0.40)
        scam_reasons.append("urgency_pressure")

    if any(x in t for x in ["crypto", "bitcoin", "wallet address"]):
        scam_score = max(scam_score, 0.55)
        scam_reasons.append("crypto_payment")

    if scam_score > 0:
        findings.append({
            "category": "scam_fraud",
            "severity": float(scam_score),
            "reasons": scam_reasons
        })
        warnings.append("Possible scam or fraud detected.")

    # -----------------------------
    # Sexual content
    # -----------------------------
    sex_score = 0.0
    sex_reasons = []

    sexual_phrases = [
        "send nudes",
        "dm for nudes",
        "private pics",
        "exclusive content",
        "hook up",
    ]

    if any(p in t for p in sexual_phrases):
        sex_score = 0.70
        sex_reasons.append("explicit_language")

    if sex_score > 0:
        findings.append({
            "category": "sexual_content",
            "severity": float(sex_score),
            "reasons": sex_reasons
        })
        warnings.append("Sexual or suggestive content detected.")

    # -----------------------------
    # Child safety
    # -----------------------------
    child_score = 0.0
    child_reasons = []

    if any(x in t for x in ["i'm 16", "i am 16", "under 18", "minor"]):
        child_score = 0.85
        child_reasons.append("minor_mentioned")

    if "meet privately" in t:
        child_score = max(child_score, 0.60)
        child_reasons.append("unsafe_meeting_context")

    if child_score > 0:
        findings.append({
            "category": "child_safety",
            "severity": float(child_score),
            "reasons": child_reasons
        })
        warnings.append("Child safety risk detected.")

    # -----------------------------
    # Overall score
    # -----------------------------
    overall = max([f.get("severity", 0.0) for f in findings], default=0.0)

    safe_to_show = True
    if overall >= 0.70:
        safe_to_show = False

    if any(
        f.get("category") == "child_safety" and f.get("severity", 0.0) >= 0.60
        for f in findings
    ):
        safe_to_show = False

    return {
        "safe_to_show": safe_to_show,
        "overall_severity": float(overall),
        "trigger_warnings": warnings,
        "findings": findings,
        "debug": {
            "locale": locale,
            "text_len": len(text or "")
        },
    }
