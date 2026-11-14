import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to MitraMaati API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_records():
    response = client.get("/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_endpoint():
    response = client.get("/search?q=Nitrogen")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_question():
    payload = {
        "farmer_name": "PRIYANKA",
        "question": "How do I manage soil nitrogen levels?"
    }
    response = client.post("/questions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_name"] == "PRIYANKA"
    assert "matched_records" in data
