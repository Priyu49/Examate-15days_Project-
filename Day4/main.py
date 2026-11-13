import json
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from Day4.smart_search import smart_search

app = FastAPI(title="MitraMaati API", version="1.0")

def load_records():
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class QuestionPayload(BaseModel):
    question: str
    farmer_name: str = "Anonymous"

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
    for r in records:
        if r.get("sample_id") == sample_id:
            return r
    raise HTTPException(status_code=404, detail="Soil record not found")

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