from models import SoilRecord
from fetch import fetch_soil_data

def ingest_records():
    raw_data = fetch_soil_data()
    validated_records = []
    for item in raw_data:
        try:
            record = SoilRecord(**item)
            validated_records.append(record)
        except Exception as e:
            print(f"Validation error for record {item.get('sample_id')}: {e}")
    return validated_records

if __name__ == "__main__":
    valid = ingest_records()
    print(f"Successfully ingested {len(valid)} soil records.")