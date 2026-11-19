import json
import os
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import agent_graph
from app.llm import get_llm_response
from app.rag import answer_question
from app.tools import classify_soil_card
from app.tools import load_records as load_soil_records
from app.vectorstore import vector_store
from smart_search import smart_search

# 1. Initialize FastAPI app first
app = FastAPI(title="MitraMaati API", version="1.0")

class AgentRequest(BaseModel):
    query: str = ""
    thread_id: str | None = None   # same thread_id = same conversation memory
    approve: bool | None = None    # True/False resumes a paused approval

class SoilCardPayload(BaseModel):
    values: dict[str, float]          # {"Nitrogen (N)": 200, "Soil pH": 6.4, ...}

class FeedbackPayload(BaseModel):
    question: str
    answer: str
    rating: str                       # "up" or "down"
    thread_id: str | None = None

class ChatPayload(BaseModel):
    message: str

class AskPayload(BaseModel):
    question: str
    top_k: int = 3

class QuestionPayload(BaseModel):
    question: str
    farmer_name: str = "Anonymous"

@app.post("/agent")
def run_agent_endpoint(req: AgentRequest):
    """
    Day 9 LangGraph agent with memory (MemorySaver + thread_id) and a real approval gate.
    - Send {query, thread_id?}: runs the graph. If a farmer approval is needed the graph
      pauses and status is "pending_approval".
    - Send {thread_id, approve: true/false}: resumes the paused graph.
    """
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    paused = bool(agent_graph.get_state(config).next)

    if req.approve is not None:
        if not paused:
            raise HTTPException(status_code=409, detail="Nothing is waiting for approval on this thread.")
        result = agent_graph.invoke(Command(resume=req.approve), config)
    else:
        if not req.query.strip():
            raise HTTPException(status_code=400, detail="query must not be empty.")
        if paused:
            raise HTTPException(status_code=409, detail="Approve or reject the pending recommendation first.")
        result = agent_graph.invoke({"query": req.query}, config)

    pending = result.get("__interrupt__")
    state = agent_graph.get_state(config).values
    return {
        "thread_id": thread_id,
        "query": req.query,
        "status": "pending_approval" if pending else "done",
        "approval_request": pending[0].value if pending else None,
        "response": state.get("response", ""),
        "approved": state.get("approved", False),
        "citations": state.get("citations", []),
        "tool_output": state.get("tool_output"),
        "turns_remembered": len(state.get("history", [])),
    }

@app.post("/soil-card")
def soil_card(payload: SoilCardPayload):
    """Classifies every entered value (Low/Medium/High + red/yellow/green) with classify_soil_card."""
    order = [r["parameter_name"] for r in load_soil_records()]
    tiles = [classify_soil_card(name, payload.values[name]) for name in order if name in payload.values]
    unknown = [k for k in payload.values if k not in order]
    return {"tiles": tiles, "unknown_parameters": unknown}

@app.post("/feedback")
def save_feedback(payload: FeedbackPayload):
    if payload.rating not in ("up", "down"):
        raise HTTPException(status_code=400, detail="rating must be 'up' or 'down'.")
    os.makedirs("data", exist_ok=True)
    row = {"time": datetime.now(UTC).isoformat(), **payload.model_dump()}
    with open(os.path.join("data", "feedback.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"saved": True}

@app.post("/chat")
def chat_endpoint(payload: ChatPayload):
    response = get_llm_response(payload.message)
    return response

@app.post("/ask")
def ask_endpoint(payload: AskPayload):
    return answer_question(payload.question, top_k=payload.top_k)

def load_records():
    path = os.path.join("data", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/records")
def get_records(limit: int = Query(None, description="Limit number of records returned")):
    records = load_records()
    if limit is not None:
        return records[:limit]
    return records

@app.get("/records/{sample_id}")
def get_record_by_id(sample_id: int):
    records = load_records()
    if 0 <= sample_id < len(records):
        return records[sample_id]
    for r in records:
        if r.get("sample_id") == sample_id:
            return r
    if records:
        return records[0]
    raise HTTPException(status_code=404, detail="Soil record not found")

@app.get("/search/semantic")
def semantic_search(q: str = Query(..., description="Semantic search query")):
    results = vector_store.similarity_search(q, top_k=3)
    return {
        "query": q,
        "hits": results
    }

@app.get("/search")
def search_records(q: str = Query("", description="Search query")):
    if not q:
        return load_records()
    return smart_search(q)

@app.post("/questions")
def post_question(payload: QuestionPayload):
    results = smart_search(payload.question)
    return {
        "farmer_name": payload.farmer_name,
        "question": payload.question,
        "matched_records": results[:2],
        "status": "Answered via RAG pipeline"
    }

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to MitraMaati API"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)