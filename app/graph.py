import os
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from app.agent_loop import run_agent_loop

class AgentState(TypedDict):
    query: str
    response: str
    approved: bool
    requires_approval: bool

def retrieve_node(state: AgentState) -> AgentState:
    res = run_agent_loop(state["query"])
    state["response"] = res.get("answer", "Processed by agent.")
    # Flag actions requiring agronomic expert review
    state["requires_approval"] = "apply" in state["query"].lower() or "recommend" in state["query"].lower()
    state["approved"] = not state["requires_approval"]
    return state

def approval_node(state: AgentState) -> AgentState:
    # Simulated human-in-the-loop approval gate
    state["approved"] = True
    return state

def should_approve(state: AgentState) -> Literal["approval", "end"]:
    if state["requires_approval"] and not state["approved"]:
        return "approval"
    return "end"

def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("approval", approval_node)
    
    workflow.set_entry_point("retrieve")
    workflow.add_conditional_edges("retrieve", should_approve, {"approval": "approval", "end": END})
    workflow.add_edge("approval", END)
    
    return workflow.compile()

agent_graph = build_agent_graph()