import logging
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

EXTRACTION_PROMPT = """You are a professional fact-checking assistant specializing in claim extraction.
Your job is to extract specific, verifiable factual claims from a given text.

Rules:
- Extract ONLY objective, verifiable facts (not opinions or predictions)
- Each claim must be self-contained and specific
- Keep claims concise (one sentence each)
- Ignore vague or subjective statements
- Return ONLY valid JSON, no markdown, no backticks

Response format:
{
  "claims": [
    {
      "claim": "specific factual claim here",
      "category": "science|politics|health|technology|economy|sports|other",
      "checkworthy": true
    }
  ],
  "total_claims": 3
}"""

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        api_key=settings.GROQ_API_KEY
    )

async def extract_claims(text: str) -> dict:
    """Extract verifiable claims from a text/article."""
    logger.info(f"Extracting claims from text ({len(text)} chars)")

    llm = get_llm()
    messages = [
        SystemMessage(content=EXTRACTION_PROMPT),
        HumanMessage(content=f"Extract all verifiable factual claims from this text:\n\n{text}")
    ]

    try:
        response = await llm.ainvoke(messages)
        raw = response.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        logger.info(f"Raw extraction response: {raw}")
        result = json.loads(raw)

        # Validate structure
        if "claims" not in result:
            raise ValueError("LLM response missing 'claims' key")

        logger.info(f"Extracted {result.get('total_claims', len(result['claims']))} claims")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e} | Raw: {raw}")
        raise ValueError(f"LLM returned invalid JSON: {raw}")
    except Exception as e:
        logger.error(f"Claim extraction failed: {e}")
        raise