import json
import os

def smart_filter(keyword: str):
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    keyword = keyword.lower()
    return [
        r for r in records 
        if keyword in r["location"].lower() or keyword in r["soil_type"].lower() or keyword in r["farmer_name"].lower()
    ]