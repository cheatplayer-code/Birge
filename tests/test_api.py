"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_status(self, client):
        """Health response should include status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_returns_version(self, client):
        """Health response should include version field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
    
    def test_health_returns_demo_mode(self, client):
        """Health response should include demo_mode field."""
        response = client.get("/health")
        data = response.json()
        assert "demo_mode" in data


class TestModelInfoEndpoint:
    """Test /model-info endpoint."""
    
    def test_model_info_returns_200(self, client):
        """Model info endpoint should return 200 OK."""
        response = client.get("/model-info")
        assert response.status_code == 200
    
    def test_model_info_returns_formula(self, client):
        """Model info should include the ranking formula."""
        response = client.get("/model-info")
        data = response.json()
        assert "formula" in data
        assert "interest_match" in data["formula"]
        assert "momentum" in data["formula"]
    
    def test_model_info_not_trained_ml(self, client):
        """Model info should indicate it's not trained ML."""
        response = client.get("/model-info")
        data = response.json()
        assert data["not_trained_ml"] is True


class TestRecommendationsEndpoint:
    """Test /recommendations endpoint."""
    
    def test_recommendations_returns_200_with_user_id(self, client):
        """Recommendations endpoint should return 200 with valid user_id."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        assert response.status_code == 200
    
    def test_recommendations_returns_success_field(self, client):
        """Recommendations response should include success field."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        assert "success" in data
        assert data["success"] is True
    
    def test_recommendations_returns_user_id(self, client):
        """Recommendations response should echo user_id."""
        response = client.get("/recommendations?user_id=test-user")
        data = response.json()
        assert "user_id" in data
    
    def test_recommendations_returns_recommendations_array(self, client):
        """Recommendations response should include recommendations array."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_recommendations_returns_model_info(self, client):
        """Recommendations response should include model_info."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        assert "model_info" in data
    
    def test_recommendations_have_score_components(self, client):
        """Each recommendation should have score components."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "score" in rec
            assert "components" in rec
            assert "interest_match" in rec["components"]
            assert "budget_fit" in rec["components"]
            assert "city_match" in rec["components"]
            assert "momentum" in rec["components"]
    
    def test_recommendations_have_why_chips(self, client):
        """Each recommendation should have explanation chips."""
        response = client.get("/recommendations?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "why" in rec
            assert isinstance(rec["why"], list)


class TestEventsEndpoint:
    """Test /events endpoint."""
    
    def test_events_post_returns_200(self, client):
        """Events endpoint should accept POST requests."""
        event = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "event_type": "click",
            "product_id": "10000000-0000-0000-0000-000000000001",
            "category": "electronics"
        }
        response = client.post("/events", json=event)
        assert response.status_code == 200
    
    def test_events_returns_success(self, client):
        """Events response should include success field."""
        event = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "event_type": "view",
            "category": "home"
        }
        response = client.post("/events", json=event)
        data = response.json()
        assert "success" in data


class TestTrustScoreEndpoint:
    """Test /trust-score endpoint."""
    
    def test_trust_score_returns_200_with_user_id(self, client):
        """Trust score endpoint should return 200 with valid user_id."""
        response = client.get("/trust-score?user_id=00000000-0000-0000-0000-000000000001")
        assert response.status_code == 200
    
    def test_trust_score_returns_success(self, client):
        """Trust score response should include success field."""
        response = client.get("/trust-score?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        assert "success" in data
    
    def test_trust_score_returns_score(self, client):
        """Trust score response should include trust_score field."""
        response = client.get("/trust-score?user_id=00000000-0000-0000-0000-000000000001")
        data = response.json()
        assert "trust_score" in data
        assert isinstance(data["trust_score"], int)
        assert 0 <= data["trust_score"] <= 100
