import json
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from smart_search import smart_search
from app.llm import get_llm_response
from app.vectorstore import vector_store
from app.rag import answer_question
from app.graph import agent_graph

# 1. Initialize FastAPI app first
app = FastAPI(title="MitraMaati API", version="1.0")

class AgentRequest(BaseModel):
    query: str

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
    Day 9 LangGraph agent endpoint with memory and approval state.
    """
    initial_state = {"query": req.query, "response": "", "approved": False, "requires_approval": False}
    final_state = agent_graph.invoke(initial_state)
    return {
        "query": req.query,
        "response": final_state["response"],
        "approved": final_state["approved"]
    }

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