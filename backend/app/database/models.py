from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, Integer
from app.database.connection import Base

class VerificationRecord(Base):
    __tablename__ = "verifications"

    id          = Column(String(36), primary_key=True)
    claim       = Column(Text, nullable=False)
    credibility = Column(String(20), nullable=False)
    summary     = Column(Text)
    confidence  = Column(Float)
    reasoning   = Column(Text)
    sources     = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)

class ClaimExtraction(Base):
    __tablename__ = "claim_extractions"

    id             = Column(String(36), primary_key=True)
    original_text  = Column(Text, nullable=False)
    claims_json    = Column(Text)
    total_claims   = Column(Integer)
    created_at     = Column(DateTime, default=datetime.utcnow)