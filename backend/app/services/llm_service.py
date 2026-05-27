import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from app.config import get_settings
from functools import lru_cache

# Force fresh settings load
get_settings.cache_clear()
settings = get_settings()

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a professional fact-checking AI assistant.
When given a news claim, you analyze it and respond ONLY with valid JSON in this exact format:
{
  "credibility": "true" | "false" | "misleading" | "unverified",
  "summary": "one sentence summary of your finding",
  "confidence_score": 0.0 to 1.0,
  "reasoning": "2-3 sentences explaining your assessment"
}
Do not include anything outside the JSON. No markdown, no backticks, just raw JSON."""

import os
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    logger.info(f"Direct os.getenv key: '{api_key[:8] if api_key else 'EMPTY'}'")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        api_key=api_key
    )

async def analyze_claim(claim: str, context: str = None) -> dict:
    logger.info(f"GROQ KEY LOADED: '{settings.GROQ_API_KEY[:8]}...'")
    logger.info(f"Analyzing claim: {claim[:80]}...")

    user_content = f"Claim: {claim}"
    if context:
        user_content += f"\nContext: {context}"

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]

    try:
        response = await llm.ainvoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        logger.info(f"LLM raw response: {raw}")
        return json.loads(raw)

    except Exception as e:
        logger.error(f"FULL ERROR TYPE: {type(e).__name__}")
        logger.error(f"FULL ERROR DETAIL: {str(e)}")
        import traceback
        logger.error(f"TRACEBACK: {traceback.format_exc()}")
        raise