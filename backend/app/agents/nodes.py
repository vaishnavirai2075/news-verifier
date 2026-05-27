import logging
from app.agents.state import AgentState
from app.services.vector_store import search_similar_claims, store_verification
from app.services.retrieval_service import retrieve_evidence
from app.services.llm_service import analyze_claim
from app.services.verification_engine import generate_report

logger = logging.getLogger(__name__)

async def cache_check_node(state: AgentState) -> AgentState:
    """Agent 1: Check vector store for cached result."""
    logger.info(f"[AGENT] Cache Check: {state['claim'][:60]}")
    state["current_step"] = "cache_check"

    try:
        cached = await search_similar_claims(state["claim"])
        if cached:
            logger.info("[AGENT] Cache HIT")
            state["cache_hit"] = True
            state["report"] = {
                "claim": state["claim"],
                "verdict": cached["credibility"],
                "confidence_score": cached["confidence_score"],
                "summary": cached["summary"],
                "reasoning": f"[CACHED] {cached['reasoning']}",
                "sources": cached["sources"],
                "contradictions": [],
                "source_consensus": "cached",
                "total_sources": len(cached["sources"]),
                "high_credibility_sources": 0,
                "report_status": "cached"
            }
        else:
            logger.info("[AGENT] Cache MISS")
            state["cache_hit"] = False
    except Exception as e:
        logger.error(f"[AGENT] Cache check failed: {e}")
        state["cache_hit"] = False
        state["error"] = str(e)

    return state

async def retrieval_node(state: AgentState) -> AgentState:
    """Agent 2: Retrieve evidence from web and news."""
    logger.info(f"[AGENT] Retrieval: {state['claim'][:60]}")
    state["current_step"] = "retrieval"

    try:
        evidence = await retrieve_evidence(state["claim"])
        state["evidence"] = evidence
        logger.info(f"[AGENT] Retrieved {len(evidence)} sources")
    except Exception as e:
        logger.error(f"[AGENT] Retrieval failed: {e}")
        state["evidence"] = []
        state["error"] = str(e)

    return state

async def analysis_node(state: AgentState) -> AgentState:
    """Agent 3: Analyze claim with LLM using evidence as context."""
    logger.info(f"[AGENT] Analysis: {state['claim'][:60]}")
    state["current_step"] = "analysis"

    try:
        evidence_text = "\n".join([
            f"- {e['title']}: {e['content']}"
            for e in state["evidence"][:5]
        ])
        result = await analyze_claim(
            state["claim"],
            context=evidence_text or state.get("context")
        )
        state["llm_result"] = result
        logger.info(f"[AGENT] Analysis done — verdict: {result['credibility']}")
    except Exception as e:
        logger.error(f"[AGENT] Analysis failed: {e}")
        state["error"] = str(e)

    return state

async def report_node(state: AgentState) -> AgentState:
    """Agent 4: Generate full verification report."""
    logger.info(f"[AGENT] Report generation")
    state["current_step"] = "report"

    try:
        report = await generate_report(
            claim=state["claim"],
            llm_result=state["llm_result"],
            raw_sources=state["evidence"][:6]
        )
        report_dict = report.model_dump()

        # Inject bias and diversity results
        report_dict["bias_analysis"] = state.get("bias_result", {
            "bias_type": "neutral",
            "bias_score": 0.0,
            "bias_indicators": [],
            "explanation": "Not analyzed"
        })
        report_dict["source_diversity"] = state.get("diversity_result", {
            "diversity_score": 0.0,
            "unique_domains": 0,
            "source_types": [],
            "recommendation": "Not analyzed"
        })

        state["report"] = report_dict
        logger.info("[AGENT] Report generated successfully")
    except Exception as e:
        logger.error(f"[AGENT] Report generation failed: {e}")
        state["error"] = str(e)

    return state

async def storage_node(state: AgentState) -> AgentState:
    """Agent 5: Store result in vector DB for future cache hits."""
    logger.info("[AGENT] Storing result in vector DB")
    state["current_step"] = "storage"

    try:
        if state.get("llm_result") and state.get("evidence") is not None:
            await store_verification(
                claim=state["claim"],
                credibility=state["llm_result"]["credibility"],
                summary=state["llm_result"]["summary"],
                confidence_score=float(state["llm_result"]["confidence_score"]),
                reasoning=state["llm_result"]["reasoning"],
                sources=state["evidence"][:5]
            )
            logger.info("[AGENT] Stored successfully")
    except Exception as e:
        logger.error(f"[AGENT] Storage failed: {e}")

    return state

async def bias_detection_node(state: AgentState) -> AgentState:
    """Agent 6: Detect political/emotional bias in the claim."""
    logger.info(f"[AGENT] Bias Detection: {state['claim'][:60]}")
    state["current_step"] = "bias_detection"

    try:
        from app.services.llm_service import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        import json

        llm = get_llm()
        system = """You are a media bias analyst. Analyze the given claim for bias.
Respond ONLY with valid JSON in this exact format:
{
  "bias_type": "political_left" | "political_right" | "emotional" | "sensational" | "neutral",
  "bias_score": 0.0 to 1.0,
  "bias_indicators": ["list", "of", "bias", "indicators"],
  "explanation": "one sentence explanation"
}
No markdown, no backticks, just raw JSON."""

        response = await llm.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Claim: {state['claim']}")
        ])

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        state["bias_result"] = json.loads(raw)
        logger.info(f"[AGENT] Bias detected: {state['bias_result']['bias_type']}")

    except Exception as e:
        logger.error(f"[AGENT] Bias detection failed: {e}")
        state["bias_result"] = {
            "bias_type": "neutral",
            "bias_score": 0.0,
            "bias_indicators": [],
            "explanation": "Bias detection unavailable"
        }

    return state


async def diversity_node(state: AgentState) -> AgentState:
    """Agent 7: Analyze source diversity."""
    logger.info("[AGENT] Source Diversity Analysis")
    state["current_step"] = "diversity"

    try:
        sources = state.get("evidence", [])
        if not sources:
            state["diversity_result"] = {
                "diversity_score": 0.0,
                "unique_domains": 0,
                "source_types": [],
                "recommendation": "No sources available"
            }
            return state

        domains = list(set([
            s.get("url", "").split("/")[2]
            for s in sources
            if s.get("url")
        ]))

        source_types = list(set([s.get("source", "unknown") for s in sources]))
        diversity_score = min(1.0, len(domains) / 5.0)

        if diversity_score >= 0.8:
            recommendation = "Excellent source diversity"
        elif diversity_score >= 0.5:
            recommendation = "Moderate source diversity"
        else:
            recommendation = "Limited source diversity — treat with caution"

        state["diversity_result"] = {
            "diversity_score": round(diversity_score, 2),
            "unique_domains": len(domains),
            "source_types": source_types,
            "recommendation": recommendation
        }
        logger.info(f"[AGENT] Diversity score: {diversity_score}")

    except Exception as e:
        logger.error(f"[AGENT] Diversity analysis failed: {e}")
        state["diversity_result"] = {
            "diversity_score": 0.0,
            "unique_domains": 0,
            "source_types": [],
            "recommendation": "Diversity analysis unavailable"
        }

    return state