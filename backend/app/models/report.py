from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class CredibilityLevel(str, Enum):
    TRUE = "true"
    FALSE = "false"
    MISLEADING = "misleading"
    UNVERIFIED = "unverified"

class ScoredSource(BaseModel):
    title: str
    url: str
    content: str
    source: str
    credibility_score: float = Field(..., ge=0.0, le=1.0)
    domain_tier: str  # "high", "medium", "low"

class Contradiction(BaseModel):
    source_a: str
    source_b: str
    description: str
    severity: str  # "high", "medium", "low"

class VerificationReport(BaseModel):
    claim: str
    verdict: CredibilityLevel
    confidence_score: float
    summary: str
    reasoning: str
    contradictions: List[Contradiction] = []
    sources: List[ScoredSource] = []
    source_consensus: str       # "strong", "moderate", "weak", "none"
    total_sources: int
    high_credibility_sources: int
    report_status: str = "completed"