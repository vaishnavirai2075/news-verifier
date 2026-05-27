import logging
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    cache_check_node,
    retrieval_node,
    analysis_node,
    report_node,
    storage_node,
    bias_detection_node,
    diversity_node
)

logger = logging.getLogger(__name__)

def should_skip_to_end(state: AgentState) -> str:
    if state.get("cache_hit"):
        return "end"
    return "retrieval"

def build_verification_graph():
    graph = StateGraph(AgentState)

    graph.add_node("cache_check", cache_check_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("bias_detection", bias_detection_node)
    graph.add_node("diversity", diversity_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("report", report_node)
    graph.add_node("storage", storage_node)

    graph.set_entry_point("cache_check")

    graph.add_conditional_edges(
        "cache_check",
        should_skip_to_end,
        {"end": END, "retrieval": "retrieval"}
    )

    # Sequential: retrieval → bias → diversity → analysis
    graph.add_edge("retrieval", "bias_detection")
    graph.add_edge("bias_detection", "diversity")
    graph.add_edge("diversity", "analysis")
    graph.add_edge("analysis", "report")
    graph.add_edge("report", "storage")
    graph.add_edge("storage", END)

    return graph.compile()

verification_graph = build_verification_graph()