import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("[INFO] Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Response: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Could not connect to FastAPI server. Make sure uvicorn is running! Error: {e}")

def ask_question(farmer_name: str, question: str):
    url = f"{BASE_URL}/questions"
    payload = {
        "farmer_name": farmer_name,
        "question": question
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("\n--- MitraMaati Advisory Response ---")
            print(f"Farmer Name : {data.get('farmer_name')}")
            print(f"Query       : {data.get('question')}")
            print(f"Status      : {data.get('status')}")
            print("Matched Records:")
            for rec in data.get('matched_records', []):
                print(f"  - Parameter: {rec.get('parameter_name')}")
                print(f"    Meaning  : {rec.get('what_it_means')}")
                print(f"    Unit     : {rec.get('unit')}")
            print("-" * 40)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

if __name__ == "__main__":
    print("=== MitraMaati Interactive Client ===")
    test_health()
    
    while True:
        print("\nOptions:")
        print("1. Ask a Soil Health Question")
        print("2. Exit")
        choice = input("Enter your choice (1-2): ").strip()
        
        if choice == "1":
            name = input("Enter your name: ").strip()
            q = input("Enter your soil question: ").strip()
            if q:
                ask_question(name, q)
        elif choice == "2":
            print("Exiting client. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")