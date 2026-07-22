from fastapi.testclient import TestClient
from sentinel.api import app

client = TestClient(app)

def test_analyze_trace_endpoint():
    payload = {
        "user_prompt": "Test prompt",
        "tool_calls": [
            {
                "tool_name": "read_file",
                "args": {"path": "test.txt"},
                "source_trust": 1.0
            }
        ]
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "result" in data
    
    result = data["result"]
    assert "sri_score" in result
    assert "decision" in result
    assert "breakdown" in result

def test_analyze_trace_invalid_payload():
    payload = {
        "user_prompt": "Test prompt"
        # missing tool_calls
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (validation error)
