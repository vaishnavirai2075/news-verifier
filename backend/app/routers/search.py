import logging
from fastapi import APIRouter, HTTPException, Query
from app.services.vector_store import search_similar_claims, get_all_verified_claims

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/similar")
async def find_similar(
    claim: str = Query(..., min_length=10, description="Claim to search for"),
    threshold: float = Query(0.85, ge=0.0, le=1.0)
):
    """Search for similar already-verified claims in vector store."""
    try:
        result = await search_similar_claims(claim, threshold)
        if result:
            return {"found": True, "result": result}
        return {"found": False, "result": None}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history(limit: int = Query(20, ge=1, le=100)):
    """Get all previously verified claims."""
    try:
        claims = await get_all_verified_claims(limit)
        return {
            "total": len(claims),
            "claims": claims
        }
    except Exception as e:
        logger.error(f"History fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))