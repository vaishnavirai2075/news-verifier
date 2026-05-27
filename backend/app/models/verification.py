from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class VerificationRequest(BaseModel):
    claim: str = Field(..., min_length=10, description="News claim or headline to verify")
    context: Optional[str] = Field(None, description="Optional additional context")

class CredibilityLevel(str, Enum):
    TRUE = "true"
    FALSE = "false"
    MISLEADING = "misleading"
    UNVERIFIED = "unverified"

class Source(BaseModel):
    title: str
    url: str
    content: str
    source: str

class VerificationResponse(BaseModel):
    claim: str
    credibility: CredibilityLevel
    summary: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    sources: List[Source] = []      # ← new
    status: str = "completed"

class ExtractionRequest(BaseModel):
    text: str = Field(..., min_length=20, description="Article or paragraph to extract claims from")

class ExtractedClaim(BaseModel):
    claim: str
    category: str
    checkworthy: bool

class ExtractionResponse(BaseModel):
    original_text: str
    claims: List[ExtractedClaim]
    total_claims: int
    status: str = "completed"