from typing import List
from app.pipeline.schemas import Finding, ModerateResponse
from app.pipeline.rules import run_rule_checks
from app.pipeline.heuristics import scam_heuristic_score, child_safety_score, sexual_score
from app.pipeline.models import model_moderation

def run_pipeline(text: str, locale: str = "en") -> ModerateResponse:
    rule_hits = run_rule_checks(text)
    model_scores = model_moderation(text, locale)

    findings: List[Finding] = []

    scam_score = scam_heuristic_score(rule_hits["scam"])
    if scam_score > 0:
        findings.append(Finding(category="scam_fraud", severity=scam_score, reasons=rule_hits["scam"]))

    child_score = child_safety_score(rule_hits["child_safety"])
    if child_score > 0:
        findings.append(Finding(category="child_safety", severity=child_score, reasons=rule_hits["child_safety"]))

    sex_score = sexual_score(rule_hits["sexual"])
    if sex_score > 0:
        findings.append(Finding(category="sexual_content", severity=sex_score, reasons=rule_hits["sexual"]))

    hate_score = max(model_scores.get("hate", 0.0), model_scores.get("harassment", 0.0))
    if hate_score > 0:
        findings.append(Finding(category="hate_harassment", severity=hate_score, reasons=["local_model_signal"]))

    overall = 0.0 if not findings else max(f.severity for f in findings)

    trigger_warnings = []
    if any(f.category == "child_safety" and f.severity >= 0.4 for f in findings):
        trigger_warnings.append("Child safety risk — may involve minors, grooming, or exploitation.")
    if any(f.category == "sexual_content" and f.severity >= 0.4 for f in findings):
        trigger_warnings.append("Sexual content — may be explicit, suggestive, or solicitation.")
    if any(f.category == "hate_harassment" and f.severity >= 0.4 for f in findings):
        trigger_warnings.append("Hate/harassment — may include hateful or abusive language.")
    if any(f.category == "scam_fraud" and f.severity >= 0.4 for f in findings):
        trigger_warnings.append("Possible scam/fraud — be cautious with links, payments, and personal info.")

    safe_to_show = not (overall >= 0.7 or any(f.category == "child_safety" and f.severity >= 0.6 for f in findings))

    return ModerateResponse(
        safe_to_show=safe_to_show,
        overall_severity=overall,
        findings=findings,
        trigger_warnings=trigger_warnings,
        debug={"rule_hits": rule_hits, "model_scores": model_scores},
    )
