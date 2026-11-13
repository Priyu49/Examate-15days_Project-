import json
import os
import requests

def fetch_soil_data():
    path = os.path.join("Day3", "records.json")
    try:
        response = requests.get("https://raw.githubusercontent.com/datasets/sindresorhus-top-repositories/master/data/repositories.json", timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Network warning (using local JSON): {e}")
        
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []