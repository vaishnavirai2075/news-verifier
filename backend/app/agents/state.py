from typing import TypedDict, List, Optional, Annotated
import operator

class AgentState(TypedDict):
    claim: str
    context: Optional[str]
    extracted_claims: List[str]
    evidence: List[dict]
    llm_result: Optional[dict]
    report: Optional[dict]
    cache_hit: bool
    error: Optional[str]
    current_step: Annotated[str, lambda a, b: b]
    # Phase 11 parallel fields
    bias_result: Optional[dict]
    diversity_result: Optional[dict]