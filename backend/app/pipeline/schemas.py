from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ModerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    locale: Optional[str] = "en"

class Finding(BaseModel):
    category: str
    severity: float
    reasons: List[str] = []

class ModerateResponse(BaseModel):
    safe_to_show: bool
    overall_severity: float
    findings: List[Finding]
    trigger_warnings: List[str]
    debug: Optional[Dict] = None
