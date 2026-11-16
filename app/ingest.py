import sys
import os

# Add parent directory to system path so 'app' can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from app.models import SoilRecord

def ingest_data():
    path = os.path.join("data", "records.json")
    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    cleaned_records = []
    for item in raw_data:
        try:
            record = SoilRecord(
                parameter_name=str(item["parameter_name"]),
                unit=str(item["unit"]),
                low_below=str(item["low_below"]),
                high_above=str(item["high_above"]),
                what_it_means=str(item["what_it_means"]),
                source_url=str(item["source_url"])
            )
            cleaned_records.append(record)
        except Exception as e:
            print(f"Skipping bad row due to error: {e}")
            
    return cleaned_records

if __name__ == "__main__":
    records = ingest_data()
    print(f"Successfully ingested {len(records)} clean records.")