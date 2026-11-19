import json

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)
REQUIRED = {"parameter_name", "unit", "low_below", "high_above", "what_it_means", "source_url"}


def load_records():
    with open("data/records.json", encoding="utf-8") as f:
        return json.load(f)


# --- records ---
def test_records_has_12_parameters():
    assert len(load_records()) == 12


def test_records_have_required_fields():
    for r in load_records():
        assert REQUIRED <= set(r)


def test_records_thresholds_make_sense():
    for r in load_records():
        assert r["low_below"] <= r["high_above"]


# --- API ---
def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_soil_card_returns_12_tiles():
    values = {r["parameter_name"]: 1.0 for r in load_records()}
    r = client.post("/soil-card", json={"values": values})
    assert r.status_code == 200
    assert len(r.json()["tiles"]) == 12


def test_feedback_rejects_bad_rating():
    r = client.post("/feedback", json={"question": "q", "answer": "a", "rating": "meh"})
    assert r.status_code == 400


# --- search ---
def test_search_returns_results():
    from smart_search import smart_search

    results = smart_search("phosphorus")
    assert len(results) > 0


# --- /ask with a fake LLM ---
def test_ask_with_fake_llm(monkeypatch):
    # rag.py does `from app.llm import generate_answer`, so patch the name inside app.rag
    monkeypatch.setattr("app.rag.generate_answer", lambda *a, **k: "FAKE ANSWER")
    r = client.post("/ask", json={"question": "What does low phosphorus mean?", "top_k": 3})
    assert r.status_code == 200
    assert "FAKE ANSWER" in json.dumps(r.json())


# --- agent tool ---
def test_agent_tool_classifies_soil_parameter():
    from app.tools import classify_soil_card

    name = load_records()[0]["parameter_name"]
    out = classify_soil_card(name, 200.0)
    assert isinstance(out, dict)
    assert "status" in out