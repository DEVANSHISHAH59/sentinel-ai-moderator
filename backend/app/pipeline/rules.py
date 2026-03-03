import re
from typing import List, Tuple, Dict

SCAM_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("payment_gift_cards", re.compile(r"\b(gift\s*card|steam\s*card|itunes\s*card)\b", re.I)),
    ("urgent_act_now", re.compile(r"\b(act\s+now|urgent|limited\s+time|final\s+notice)\b", re.I)),
    ("crypto_payment", re.compile(r"\b(bitcoin|btc|usdt|wallet\s+address)\b", re.I)),
    ("impersonation", re.compile(r"\b(verify\s+your\s+account|account\s+will\s+be\s+closed)\b", re.I)),
    ("too_good_to_be_true", re.compile(r"\b(guaranteed\s+profit|double\s+your\s+money|100%\s+returns)\b", re.I)),
]

SEXUAL_HINT_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("explicit_solicitation", re.compile(r"\b(send\s+nudes|hook\s*up\s+now|dm\s+for\s+sex)\b", re.I)),
]

CHILD_SAFETY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("minor_age_mentions", re.compile(r"\b(i'?m\s+)?(1[0-7]|under\s*18)\b", re.I)),
    ("adult_minor_context", re.compile(r"\b(older\s+men|older\s+women|age\s+gap)\b", re.I)),
]

def run_rule_checks(text: str) -> Dict[str, list]:
    hits = {"scam": [], "sexual": [], "child_safety": []}
    for name, pat in SCAM_PATTERNS:
        if pat.search(text):
            hits["scam"].append(name)
    for name, pat in SEXUAL_HINT_PATTERNS:
        if pat.search(text):
            hits["sexual"].append(name)
    for name, pat in CHILD_SAFETY_PATTERNS:
        if pat.search(text):
            hits["child_safety"].append(name)
    return hits
