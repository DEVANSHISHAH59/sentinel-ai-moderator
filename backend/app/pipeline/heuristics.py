from typing import List

def scam_heuristic_score(hits: List[str]) -> float:
    score = 0.0
    score += 0.35 if "payment_gift_cards" in hits else 0.0
    score += 0.25 if "crypto_payment" in hits else 0.0
    score += 0.20 if "urgent_act_now" in hits else 0.0
    score += 0.20 if "impersonation" in hits else 0.0
    score += 0.15 if "too_good_to_be_true" in hits else 0.0
    return min(score, 1.0)

def child_safety_score(hits: List[str]) -> float:
    score = 0.0
    score += 0.60 if "minor_age_mentions" in hits else 0.0
    score += 0.20 if "adult_minor_context" in hits else 0.0
    return min(score, 1.0)

def sexual_score(hits: List[str]) -> float:
    return 0.55 if "explicit_solicitation" in hits else 0.0
