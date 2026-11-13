import os
import json
import pandas as pd

def explore_soil_data():
    path = os.path.join("data", "records.json")
    if not os.path.exists(path):
        print("No data available.")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # Automatically detect the correct column name for parameters
    col_name = 'parameter_name' if 'parameter_name' in df.columns else (df.columns[0] if len(df.columns) > 0 else None)
    
    print("--- MitraMaati Pandas Facts ---")
    print(f"Fact 1: Total records tracked in dataset is {len(df)}.")
    print(f"Fact 2: Number of columns available is {len(df.columns)}.")
    if col_name:
        print(f"Fact 3: Average string length of '{col_name}' values is {df[col_name].astype(str).str.len().mean():.1f} characters.")
    else:
        print("Fact 3: Dataset loaded successfully.")

if __name__ == "__main__":
    explore_soil_data()