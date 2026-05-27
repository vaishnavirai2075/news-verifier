import logging
import json
import chromadb
from chromadb.utils import embedding_functions
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Collection name
COLLECTION_NAME = "verified_claims"

def get_chroma_client():
    """Get persistent ChromaDB client."""
    return chromadb.PersistentClient(path="./chroma_db")

def get_collection():
    """Get or create the verified claims collection."""
    client = get_chroma_client()
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

async def store_verification(
    claim: str,
    credibility: str,
    summary: str,
    confidence_score: float,
    reasoning: str,
    sources: list
) -> str:
    """Store a verified claim in ChromaDB."""
    import uuid
    claim_id = str(uuid.uuid4())

    logger.info(f"Storing verification for: {claim[:60]}")

    try:
        collection = get_collection()
        collection.add(
            ids=[claim_id],
            documents=[claim],
            metadatas=[{
                "credibility": credibility,
                "summary": summary,
                "confidence_score": confidence_score,
                "reasoning": reasoning,
                "sources": json.dumps(sources)
            }]
        )
        logger.info(f"Stored claim with ID: {claim_id}")
        return claim_id

    except Exception as e:
        logger.error(f"Failed to store verification: {e}")
        raise

async def search_similar_claims(claim: str, threshold: float = 0.85) -> dict | None:
    """
    Search for a similar already-verified claim.
    Returns cached result if similarity >= threshold, else None.
    """
    logger.info(f"Searching similar claims for: {claim[:60]}")

    try:
        collection = get_collection()

        # Check if collection is empty
        if collection.count() == 0:
            logger.info("Vector store is empty — no cached results")
            return None

        results = collection.query(
            query_texts=[claim],
            n_results=1,
            include=["documents", "metadatas", "distances"]
        )

        if not results["ids"][0]:
            return None

        # ChromaDB cosine distance: 0 = identical, 1 = opposite
        # Convert to similarity score
        distance = results["distances"][0][0]
        similarity = 1 - distance

        logger.info(f"Best match similarity: {similarity:.3f} (threshold: {threshold})")

        if similarity >= threshold:
            meta = results["metadatas"][0][0]
            matched_claim = results["documents"][0][0]
            logger.info(f"Cache HIT — returning stored result")
            return {
                "matched_claim": matched_claim,
                "similarity": round(similarity, 3),
                "credibility": meta["credibility"],
                "summary": meta["summary"],
                "confidence_score": meta["confidence_score"],
                "reasoning": meta["reasoning"],
                "sources": json.loads(meta["sources"])
            }

        logger.info("Cache MISS — similarity below threshold")
        return None

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return None

async def get_all_verified_claims(limit: int = 20) -> list:
    """Retrieve all stored verified claims."""
    try:
        collection = get_collection()
        count = collection.count()

        if count == 0:
            return []

        results = collection.get(
            limit=min(limit, count),
            include=["documents", "metadatas"]
        )

        claims = []
        for i, doc in enumerate(results["documents"]):
            meta = results["metadatas"][i]
            claims.append({
                "id": results["ids"][i],
                "claim": doc,
                "credibility": meta["credibility"],
                "summary": meta["summary"],
                "confidence_score": meta["confidence_score"]
            })

        return claims

    except Exception as e:
        logger.error(f"Failed to fetch claims: {e}")
        return []