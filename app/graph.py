import operator
from typing import Annotated, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.agent_loop import run_agent_loop
from app.tools import classify_soil_card, parse_soil_query

APPROVAL_KEYWORDS = ("apply", "recommend", "fertilizer", "fertiliser", "dose")


class AgentState(TypedDict, total=False):
    query: str
    response: str
    citations: list
    tool_output: Optional[dict]
    approved: bool
    requires_approval: bool
    # Conversation memory: every finished turn is appended (kept per thread_id by the checkpointer)
    history: Annotated[list, operator.add]


def route_query(state: AgentState) -> Literal["classify", "retrieve"]:
    """Entry router: a parameter + number goes to the classify_soil_card tool, the rest to RAG."""
    return "classify" if parse_soil_query(state["query"]) else "retrieve"


def classify_node(state: AgentState) -> dict:
    name, value = parse_soil_query(state["query"])
    result = classify_soil_card(name, value)
    # A Low/High reading changes the fertilizer dose, so a human must approve it
    needs_approval = result["status"] in ("Low", "High") or any(
        k in state["query"].lower() for k in APPROVAL_KEYWORDS
    )
    return {
        "tool_output": result,
        "response": f"{result['parameter']} = {value} {result.get('unit', '')}: {result['recommendation']}",
        "citations": [{"title": result["parameter"], "page": result.get("page", 1),
                       "source": result.get("source_url", "")}],
        "requires_approval": needs_approval,
        "approved": not needs_approval,
    }


def retrieve_node(state: AgentState) -> dict:
    res = run_agent_loop(state["query"])
    needs_approval = any(k in state["query"].lower() for k in APPROVAL_KEYWORDS)
    return {
        "tool_output": res.get("tool_output"),
        "response": res.get("answer", "Processed by agent."),
        "citations": res.get("citations", []),
        "requires_approval": needs_approval,
        "approved": not needs_approval,
    }


def approval_node(state: AgentState) -> dict:
    # Human-in-the-loop: the graph PAUSES here and the checkpointer saves its state.
    # It continues only when the caller resumes with Command(resume=True/False).
    decision = interrupt({
        "question": "Farmer approval needed before this recommendation is released.",
        "proposed_response": state["response"],
    })
    approved = bool(decision.get("approved")) if isinstance(decision, dict) else bool(decision)
    if approved:
        return {"approved": True}
    return {"approved": False, "response": "Recommendation withheld: the farmer did not approve it."}


def finalize_node(state: AgentState) -> dict:
    return {"history": [{"query": state["query"], "response": state["response"],
                         "approved": state.get("approved", False)}]}


def should_approve(state: AgentState) -> Literal["approval", "finalize"]:
    if state.get("requires_approval") and not state.get("approved"):
        return "approval"
    return "finalize"


def build_agent_graph(checkpointer=None):
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_conditional_entry_point(route_query, {"classify": "classify", "retrieve": "retrieve"})
    for node in ("classify", "retrieve"):
        workflow.add_conditional_edges(node, should_approve, {"approval": "approval", "finalize": "finalize"})
    workflow.add_edge("approval", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile(checkpointer=checkpointer or MemorySaver())


agent_graph = build_agent_graph()
