import logging
import json
from urllib.parse import urlparse
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings
from app.models.report import ScoredSource, Contradiction, VerificationReport, CredibilityLevel

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Domain credibility tiers ──────────────────────────────
HIGH_CREDIBILITY_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "npr.org", "pbs.org", "theguardian.com", "nytimes.com",
    "washingtonpost.com", "economist.com", "nature.com",
    "science.org", "who.int", "cdc.gov", "nih.gov",
    "nasa.gov", "gov.uk", "un.org", "britannica.com"
}

MEDIUM_CREDIBILITY_DOMAINS = {
    "forbes.com", "time.com", "newsweek.com", "theatlantic.com",
    "wired.com", "techcrunch.com", "arstechnica.com", "cnbc.com",
    "cnn.com", "nbcnews.com", "cbsnews.com", "abcnews.go.com",
    "usatoday.com", "politico.com", "thehill.com", "axios.com"
}

def score_domain(url: str) -> tuple[float, str]:
    """Score a URL's credibility based on domain tier."""
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace("www.", "")

        if any(d in domain for d in HIGH_CREDIBILITY_DOMAINS):
            return 0.9, "high"
        elif any(d in domain for d in MEDIUM_CREDIBILITY_DOMAINS):
            return 0.65, "medium"
        else:
            return 0.4, "low"
    except:
        return 0.3, "low"

def score_sources(raw_sources: list) -> list[ScoredSource]:
    """Score each source for credibility."""
    scored = []
    for s in raw_sources:
        score, tier = score_domain(s.get("url", ""))
        scored.append(ScoredSource(
            title=s.get("title", ""),
            url=s.get("url", ""),
            content=s.get("content", ""),
            source=s.get("source", ""),
            credibility_score=score,
            domain_tier=tier
        ))
    return scored

def get_source_consensus(scored_sources: list[ScoredSource]) -> str:
    """Determine overall consensus strength from sources."""
    if not scored_sources:
        return "none"
    high = sum(1 for s in scored_sources if s.domain_tier == "high")
    if high >= 3:
        return "strong"
    elif high >= 1:
        return "moderate"
    elif len(scored_sources) >= 2:
        return "weak"
    return "none"

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        api_key=settings.GROQ_API_KEY
    )

async def detect_contradictions(
    claim: str,
    sources: list[ScoredSource]
) -> list[Contradiction]:
    """Use LLM to detect contradictions across sources."""
    if len(sources) < 2:
        return []

    logger.info("Running contradiction detection...")

    source_texts = "\n".join([
        f"Source {i+1} ({s.domain_tier} credibility): {s.title} — {s.content[:300]}"
        for i, s in enumerate(sources[:5])
    ])

    prompt = f"""Analyze these sources about the claim: "{claim}"

Sources:
{source_texts}

Find any contradictions between these sources.
Respond ONLY with valid JSON, no markdown:
{{
  "contradictions": [
    {{
      "source_a": "Source 1 title",
      "source_b": "Source 2 title",
      "description": "What they disagree on",
      "severity": "high|medium|low"
    }}
  ]
}}
If no contradictions found, return: {{"contradictions": []}}"""

    try:
        llm = get_llm()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        contradictions = [
            Contradiction(**c) for c in data.get("contradictions", [])
        ]
        logger.info(f"Found {len(contradictions)} contradictions")
        return contradictions

    except Exception as e:
        logger.error(f"Contradiction detection failed: {e}")
        return []

async def generate_report(
    claim: str,
    llm_result: dict,
    raw_sources: list
) -> VerificationReport:
    """Full verification pipeline — scores, contradictions, report."""
    logger.info(f"Generating verification report for: {claim[:60]}")

    # Step 1: Score sources
    scored_sources = score_sources(raw_sources)
    logger.info(f"Scored {len(scored_sources)} sources")

    # Step 2: Detect contradictions
    contradictions = await detect_contradictions(claim, scored_sources)

    # Step 3: Compute metrics
    high_cred = sum(1 for s in scored_sources if s.domain_tier == "high")
    consensus = get_source_consensus(scored_sources)

    # Step 4: Adjust confidence based on source quality
    base_confidence = float(llm_result["confidence_score"])
    if high_cred >= 2:
        adjusted_confidence = min(base_confidence + 0.05, 1.0)
    elif high_cred == 0 and len(scored_sources) > 0:
        adjusted_confidence = max(base_confidence - 0.1, 0.0)
    else:
        adjusted_confidence = base_confidence

    # Step 5: Build report
    report = VerificationReport(
        claim=claim,
        verdict=CredibilityLevel(llm_result["credibility"]),
        confidence_score=round(adjusted_confidence, 3),
        summary=llm_result["summary"],
        reasoning=llm_result["reasoning"],
        contradictions=contradictions,
        sources=scored_sources,
        source_consensus=consensus,
        total_sources=len(scored_sources),
        high_credibility_sources=high_cred,
        report_status="completed"
    )

    logger.info(f"Report generated — verdict: {report.verdict}, consensus: {consensus}")
    return report