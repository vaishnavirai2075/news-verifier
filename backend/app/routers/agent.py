import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.verification import VerificationRequest
from app.agents.graph import verification_graph
from app.database.connection import get_db
from app.database.db_service import save_verification, get_verification_history

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/verify")
async def agent_verify(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        initial_state = {
            "claim": request.claim,
            "context": request.context,
            "extracted_claims": [],
            "evidence": [],
            "llm_result": None,
            "report": None,
            "cache_hit": False,
            "error": None,
            "current_step": "start"
        }

        result = await verification_graph.ainvoke(initial_state)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        report = result.get("report", {})

        # Save to PostgreSQL
        await save_verification(
            db=db,
            claim=request.claim,
            credibility=report.get("verdict", "unverified"),
            summary=report.get("summary", ""),
            confidence=report.get("confidence_score", 0.0),
            reasoning=report.get("reasoning", ""),
            sources=report.get("sources", [])
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        records = await get_verification_history(db, limit=limit, offset=offset)
        return {
            "total": len(records),
            "records": records
        }
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))