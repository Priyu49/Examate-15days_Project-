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

def test_semantic_search_endpoint():
    response = client.get("/search/semantic?q=Organic%20Carbon")
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert len(data["hits"]) > 0

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

def test_ask_endpoint_with_citations():
    response = client.post("/ask", json={"question": "What is soil organic carbon?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0

def test_ask_endpoint_q6_unanswerable():
    response = client.post("/ask", json={"question": "What is the exact market price of Urea fertilizer in cooperative stores across Pune today?"})
    assert response.status_code == 200
    data = response.json()
    assert "I don't know" in data["answer"]
    assert data["citations"] == []