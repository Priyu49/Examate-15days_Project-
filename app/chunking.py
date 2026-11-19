import json
import os


def chunk_records():
    path = os.path.join("data", "records.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    chunks = []
    for idx, r in enumerate(records):
        chunk = {
            "id": f"chunk_{idx+1}",
            "source": r.get("source_url", "Soil Health Manual"),
            "page": 1,
            "title": r.get("parameter_name", "Soil Parameter"),
            "text": f"Parameter: {r.get('parameter_name')}. Unit: {r.get('unit')}. Ideal Range: {r.get('low_below')} - {r.get('high_above')}. Meaning: {r.get('what_it_means')}"
        }
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    print(f"Generated {len(chunk_records())} document chunks.")