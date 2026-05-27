import logging
from fastapi import APIRouter, HTTPException
from app.models.verification import ExtractionRequest, ExtractionResponse, ExtractedClaim
from app.services.claim_extractor import extract_claims

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("/extract", response_model=ExtractionResponse)
async def extract(request: ExtractionRequest):
    logger.info(f"Extraction request received ({len(request.text)} chars)")

    try:
        result = await extract_claims(request.text)

        claims = [
            ExtractedClaim(
                claim=c["claim"],
                category=c.get("category", "other"),
                checkworthy=c.get("checkworthy", True)
            )
            for c in result["claims"]
        ]

        return ExtractionResponse(
            original_text=request.text,
            claims=claims,
            total_claims=len(claims)
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Extraction failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))