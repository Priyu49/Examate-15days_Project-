import json
import os

def fetch_soil_data():
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)