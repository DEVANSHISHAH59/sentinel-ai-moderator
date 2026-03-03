from typing import Dict
from transformers import pipeline

toxicity_model = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    truncation=True
)

def model_moderation(text: str, locale: str = "en") -> Dict[str, float]:
    r = toxicity_model(text)[0]
    label = str(r.get("label", "")).lower()
    score = float(r.get("score", 0.0))

    hate = 0.0
    harassment = 0.0

    if "toxic" in label:
        harassment = max(harassment, score)
    if "severe" in label:
        hate = max(hate, score)

    return {
        "hate": hate,
        "harassment": harassment,
        "sexual": 0.0,
        "child_sexual_content": 0.0,
        "violence": 0.0,
        "self_harm": 0.0,
    }
