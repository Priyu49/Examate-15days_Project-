import json
import os
from fastapi import FastAPI, HTTPException

app = FastAPI(title="MitraMaati API", version="1.0")

def load_records():
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "MitraMaati"}

@app.get("/records")
def get_records():
    return load_records()

@app.get("/records/{sample_id}")
def get_record_by_id(sample_id: int):
    records = load_records()
    for r in records:
        if r["sample_id"] == sample_id:
            return r
    raise HTTPException(status_code=404, detail="Soil record not found")

@app.get("/search")
def search_records(location: str = None, soil_type: str = None):
    records = load_records()
    results = records
    if location:
        results = [r for r in results if r["location"].lower() == location.lower()]
    if soil_type:
        results = [r for r in results if r["soil_type"].lower() == soil_type.lower()]
    return results

@app.get("/recommendations/{sample_id}")
def get_recommendations(sample_id: int):
    records = load_records()
    target = None
    for r in records:
        if r["sample_id"] == sample_id:
            target = r
            break
    if not target:
        raise HTTPException(status_code=404, detail="Record not found")
    
    advice = "Balanced soil condition."
    if target["ph"] < 6.0:
        advice = "Soil is acidic. Recommend adding agricultural lime."
    elif target["ph"] > 8.0:
        advice = "Soil is alkaline. Recommend adding gypsum or organic matter."
        
    return {"sample_id": sample_id, "ph": target["ph"], "recommendation": advice}