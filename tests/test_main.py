"""
Automated tests for FAQ Chatbot API.
Uses pytest and httpx for async testing.
Run with: pytest tests/ -v
"""

import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


@pytest.fixture
def expected_faq_count():
    """Expected number of FAQ entries."""
    return 15


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_returns_200(self):
        """Test that /health returns 200 OK status."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_returns_healthy_status(self):
        """Test that /health returns healthy status."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ready"] is True
    
    @pytest.mark.asyncio
    async def test_health_shows_faq_loaded(self, expected_faq_count):
        """Test that /health shows FAQ is loaded."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
        
        data = response.json()
        assert data["faq_loaded"] is True
        assert data["faq_count"] == expected_faq_count


class TestChatEndpoint:
    """Tests for /chat endpoint."""
    
    @pytest.mark.asyncio
    async def test_chat_returns_answer(self):
        """Test that /chat returns an answer."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={"question": "What are your business hours?"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0
    
    @pytest.mark.asyncio
    async def test_chat_returns_confidence(self):
        """Test that /chat returns confidence score."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={"question": "What are your business hours?"}
            )
        
        data = response.json()
        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_chat_matches_known_question(self):
        """Test that /chat correctly matches a known question."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={"question": "What are your business hours?"}
            )
        
        data = response.json()
        # Should have high confidence for exact match
        assert data["confidence"] >= 0.3
        assert "business hours" in data["answer"].lower() or "9:00" in data["answer"]
    
    @pytest.mark.asyncio
    async def test_chat_handles_unknown_question(self):
        """Test that /chat handles unknown questions gracefully."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={"question": "xyzabc123 unknown random question"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # Should return fallback response
        assert "sorry" in data["answer"].lower() or "don't" in data["answer"].lower()
    
    @pytest.mark.asyncio
    async def test_chat_rejects_empty_question(self):
        """Test that /chat rejects empty questions."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={"question": ""}
            )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_chat_fuzzy_matching(self):
        """Test that fuzzy matching works for typos."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Slightly misspelled question
            response = await client.post(
                "/chat",
                json={"question": "What are your busines hours?"}  # missing 's' in business
            )
        
        data = response.json()
        # Should still match due to fuzzy matching
        assert data["confidence"] > 0.0


class TestRootEndpoint:
    """Tests for root / endpoint."""
    
    @pytest.mark.asyncio
    async def test_root_returns_html(self):
        """Test that root returns HTML content."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    @pytest.mark.asyncio
    async def test_root_contains_chat_elements(self):
        """Test that root HTML contains chat UI elements."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/")
        
        html_content = response.text
        assert "chat" in html_content.lower()
        assert "message" in html_content.lower()


class TestValidateEndpoint:
    """Tests for /validate endpoint."""
    
    @pytest.mark.asyncio
    async def test_validate_returns_detailed_info(self):
        """Test that /validate returns detailed match info."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/validate",
                json={"question": "How do I track my order?"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence_score" in data
        assert "confidence_label" in data
        assert "match_found" in data


class TestLogsEndpoint:
    """Tests for /logs endpoint."""
    
    @pytest.mark.asyncio
    async def test_logs_returns_list(self):
        """Test that /logs returns a list of logs."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/logs")
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "statistics" in data
        assert isinstance(data["logs"], list)


class TestServerStartup:
    """Tests for server startup."""
    
    @pytest.mark.asyncio
    async def test_server_starts_successfully(self):
        """Test that the server starts and responds to requests."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Make any request to verify server is running
            response = await client.get("/health")
        
        assert response.status_code == 200


# Run tests with: pytest tests/test_main.py -v
# For coverage: pytest tests/ -v --cov=app --cov-report=term-missing
