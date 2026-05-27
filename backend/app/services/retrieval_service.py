import logging
import httpx
from tavily import TavilyClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def get_tavily_client():
    return TavilyClient(api_key=settings.TAVILY_API_KEY)

async def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search web for evidence using Tavily."""
    logger.info(f"Tavily search: {query[:60]}")
    try:
        client = get_tavily_client()
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],  # truncate
                "source": "tavily"
            })
        logger.info(f"Tavily returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []

async def search_newsapi(query: str, max_results: int = 5) -> list[dict]:
    """Search news articles using NewsAPI."""
    logger.info(f"NewsAPI search: {query[:60]}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "apiKey": settings.NEWS_API_KEY,
                    "pageSize": max_results,
                    "sortBy": "relevancy",
                    "language": "en"
                },
                timeout=10.0
            )
            data = response.json()

            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []

            results = []
            for article in data.get("articles", []):
                results.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "content": (article.get("description") or "")[:500],
                    "source": article.get("source", {}).get("name", "newsapi")
                })
            logger.info(f"NewsAPI returned {len(results)} results")
            return results
    except Exception as e:
        logger.error(f"NewsAPI search failed: {e}")
        return []

async def retrieve_evidence(claim: str) -> list[dict]:
    """Fetch evidence from all sources for a claim."""
    logger.info(f"Retrieving evidence for: {claim[:60]}")

    tavily_results = await search_tavily(claim)
    news_results = await search_newsapi(claim)

    all_results = tavily_results + news_results

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    logger.info(f"Total unique sources: {len(unique)}")
    return unique