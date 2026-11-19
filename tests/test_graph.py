import pytest
from langgraph.types import Command

import app.graph as graph_module
from app.graph import build_agent_graph
from app.tools import classify_soil_card, parse_soil_query


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(graph_module, "run_agent_loop", lambda q: {
        "answer": "RAG answer", "citations": [{"title": "Zinc (Zn)", "page": 1, "source": "x"}], "tool_output": None})
    return build_agent_graph()


def cfg(thread):
    return {"configurable": {"thread_id": thread}}


def test_parse_soil_query():
    assert parse_soil_query("classify nitrogen 200") == ("Nitrogen (N)", 200.0)
    assert parse_soil_query("my pH is 5.5") == ("Soil pH", 5.5)
    assert parse_soil_query("what does zinc do") is None


def test_traffic_light_colours():
    assert classify_soil_card("Nitrogen (N)", 100)["color_code"] == "red"
    assert classify_soil_card("Nitrogen (N)", 400)["color_code"] == "yellow"
    assert classify_soil_card("Nitrogen (N)", 700)["color_code"] == "green"


def test_low_value_routes_to_tool_and_pauses_for_approval(agent):
    result = agent.invoke({"query": "classify nitrogen 200"}, cfg("a"))
    assert "__interrupt__" in result                       # paused, not auto-approved
    assert agent.get_state(cfg("a")).next == ("approval",)
    assert agent.get_state(cfg("a")).values["tool_output"]["status"] == "Low"


def test_resume_approve_and_reject(agent):
    agent.invoke({"query": "classify phosphorus 5"}, cfg("yes"))
    assert agent.invoke(Command(resume=True), cfg("yes"))["approved"] is True
    agent.invoke({"query": "classify phosphorus 5"}, cfg("no"))
    rejected = agent.invoke(Command(resume=False), cfg("no"))
    assert rejected["approved"] is False and "withheld" in rejected["response"]


def test_medium_value_needs_no_approval(agent):
    result = agent.invoke({"query": "classify nitrogen 300"}, cfg("m"))
    assert "__interrupt__" not in result and result["approved"] is True


def test_memory_is_kept_per_thread_id(agent):
    agent.invoke({"query": "what is zinc"}, cfg("t1"))
    second = agent.invoke({"query": "and boron?"}, cfg("t1"))
    assert len(second["history"]) == 2
    assert len(agent.invoke({"query": "what is zinc"}, cfg("t2"))["history"]) == 1
