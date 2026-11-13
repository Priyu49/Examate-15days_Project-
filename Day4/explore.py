import os
import json
import pandas as pd

def explore_soil_data():
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        print("No data available.")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    print("--- MitraMaati Pandas Facts ---")
    print(f"Fact 1: Total parameters tracked in dataset is {len(df)}.")
    print(f"Fact 2: Number of unique parameters is {df['parameter_name'].nunique() if 'parameter_name' in df else df.shape[0]}.")
    print(f"Fact 3: Average record sample ID value is {df['sample_id'].mean():.1f}.")

if __name__ == "__main__":
    explore_soil_data()