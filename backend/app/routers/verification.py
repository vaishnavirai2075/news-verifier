import logging
from fastapi import APIRouter, HTTPException
from app.models.verification import VerificationRequest, VerificationResponse, Source
from app.services.llm_service import analyze_claim
from app.services.retrieval_service import retrieve_evidence
from app.services.vector_store import search_similar_claims, store_verification
from app.services.verification_engine import generate_report
from app.models.report import VerificationReport

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/verify", tags=["Verification"])

@router.post("/", response_model=VerificationResponse)
async def verify_claim(request: VerificationRequest):
    logger.info(f"Received verification request for: {request.claim[:60]}...")

    try:
        # Step 1: Check vector store for cached result
        cached = await search_similar_claims(request.claim)
        if cached:
            logger.info("Returning cached verification result")
            sources = [Source(**s) for s in cached["sources"]] if cached["sources"] else []
            return VerificationResponse(
                claim=request.claim,
                credibility=cached["credibility"],
                summary=cached["summary"],
                confidence_score=cached["confidence_score"],
                reasoning=f"[CACHED] {cached['reasoning']}",
                sources=sources,
                status="cached"
            )

        # Step 2: Retrieve fresh evidence
        evidence = await retrieve_evidence(request.claim)

        # Step 3: Build context from evidence
        evidence_text = "\n".join([
            f"- {e['title']}: {e['content']}" for e in evidence[:5]
        ])

        # Step 4: Analyze with LLM
        result = await analyze_claim(
            request.claim,
            context=evidence_text or request.context
        )

        # Step 5: Store result in vector DB
        sources = evidence[:5]
        await store_verification(
            claim=request.claim,
            credibility=result["credibility"],
            summary=result["summary"],
            confidence_score=float(result["confidence_score"]),
            reasoning=result["reasoning"],
            sources=sources
        )

        return VerificationResponse(
            claim=request.claim,
            credibility=result["credibility"],
            summary=result["summary"],
            confidence_score=result["confidence_score"],
            reasoning=result["reasoning"],
            sources=[Source(**s) for s in sources],
            status="completed"
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"ROUTER ERROR: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/report", response_model=VerificationReport)
async def verify_with_report(request: VerificationRequest):
    """Full verification with scored sources, contradictions, and report."""
    logger.info(f"Report request for: {request.claim[:60]}...")

    try:
        # Step 1: Retrieve evidence
        evidence = await retrieve_evidence(request.claim)

        # Step 2: Build context
        evidence_text = "\n".join([
            f"- {e['title']}: {e['content']}" for e in evidence[:5]
        ])

        # Step 3: LLM analysis
        result = await analyze_claim(
            request.claim,
            context=evidence_text or request.context
        )

        # Step 4: Generate full report
        report = await generate_report(
            claim=request.claim,
            llm_result=result,
            raw_sources=evidence[:6]
        )

        # Step 5: Store in vector DB
        await store_verification(
            claim=request.claim,
            credibility=result["credibility"],
            summary=result["summary"],
            confidence_score=float(result["confidence_score"]),
            reasoning=result["reasoning"],
            sources=evidence[:5]
        )

        return report

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Report generation failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))