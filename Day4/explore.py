import os
import json
import pandas as pd

def explore_soil_data():
    path = os.path.join("Day3", "records.json")
    if not os.path.exists(path):
        print("No data available for analysis.")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    print("--- Soil Dataset Summary ---")
    print(df.describe())
    print("\nAverage pH and Nutrients by Soil Type:")
    print(df.groupby("soil_type")[["ph", "nitrogen", "phosphorus", "potassium"]].mean())

if __name__ == "__main__":
    explore_soil_data()