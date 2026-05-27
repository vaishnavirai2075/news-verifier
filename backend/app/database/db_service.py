import logging
import json
import uuid
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import VerificationRecord, ClaimExtraction

logger = logging.getLogger(__name__)

async def save_verification(
    db: AsyncSession,
    claim: str,
    credibility: str,
    summary: str,
    confidence: float,
    reasoning: str,
    sources: list
) -> str:
    record_id = str(uuid.uuid4())
    record = VerificationRecord(
        id=record_id,
        claim=claim,
        credibility=credibility,
        summary=summary,
        confidence=confidence,
        reasoning=reasoning,
        sources=json.dumps(sources),
        created_at=datetime.utcnow()
    )
    db.add(record)
    await db.commit()
    logger.info(f"Saved verification {record_id} to DB")
    return record_id

async def get_verification_history(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0
) -> list:
    result = await db.execute(
        select(VerificationRecord)
        .order_by(desc(VerificationRecord.created_at))
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "claim": r.claim,
            "credibility": r.credibility,
            "summary": r.summary,
            "confidence": r.confidence,
            "reasoning": r.reasoning,
            "sources": json.loads(r.sources) if r.sources else [],
            "created_at": r.created_at.isoformat()
        }
        for r in rows
    ]

async def get_verification_by_id(db: AsyncSession, record_id: str) -> dict | None:
    result = await db.execute(
        select(VerificationRecord).where(VerificationRecord.id == record_id)
    )
    r = result.scalar_one_or_none()
    if not r:
        return None
    return {
        "id": r.id,
        "claim": r.claim,
        "credibility": r.credibility,
        "summary": r.summary,
        "confidence": r.confidence,
        "reasoning": r.reasoning,
        "sources": json.loads(r.sources) if r.sources else [],
        "created_at": r.created_at.isoformat()
    }

async def save_extraction(
    db: AsyncSession,
    original_text: str,
    claims: list,
    total_claims: int
) -> str:
    record_id = str(uuid.uuid4())
    record = ClaimExtraction(
        id=record_id,
        original_text=original_text,
        claims_json=json.dumps(claims),
        total_claims=total_claims,
        created_at=datetime.utcnow()
    )
    db.add(record)
    await db.commit()
    return record_id