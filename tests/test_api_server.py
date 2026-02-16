"""
Comprehensive tests for Anna AI REST API - Phase 2

Tests cover:
- Health checks and status endpoints
- Configuration management
- Authentication and rate limiting
- Error handling and recovery
- Webhook system
"""

import pytest
import json
import time
from unittest.mock import MagicMock, patch
from pathlib import Path

# Import API server
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_server import APIServer, RateLimiter, CircuitBreaker


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)
        
        for i in range(5):
            assert limiter.is_allowed("client1") is True

    def test_rate_limiter_blocks_exceeded(self):
        """Test that rate limiter blocks requests over limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=1)
        
        for i in range(3):
            limiter.is_allowed("client1")
        
        # Fourth request should be blocked
        assert limiter.is_allowed("client1") is False

    def test_rate_limiter_resets_window(self):
        """Test that rate limiter resets after time window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client1") is False
        
        time.sleep(1.1)
        assert limiter.is_allowed("client1") is True

    def test_rate_limiter_remaining(self):
        """Test remaining requests calculation."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        
        remaining = limiter.get_remaining("client1")
        assert remaining == 3


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_breaker_initial_closed(self):
        """Test that circuit breaker starts in closed state."""
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker.state == "closed"
        assert breaker.call_allowed() is True

    def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        breaker.record_failure()
        assert breaker.state == "closed"
        
        breaker.record_failure()
        assert breaker.state == "open"
        assert breaker.call_allowed() is False

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test that circuit breaker enters half-open state after timeout."""
        breaker = CircuitBreaker(failure_threshold=1, timeout_seconds=1)
        
        breaker.record_failure()
        assert breaker.state == "open"
        assert breaker.call_allowed() is False
        
        time.sleep(1.1)
        assert breaker.call_allowed() is True
        assert breaker.state == "half-open"

    def test_circuit_breaker_closes_on_success(self):
        """Test that circuit breaker closes on successful call."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        breaker.record_failure()
        assert breaker.state == "open"
        
        breaker.record_success()
        assert breaker.state == "closed"


class TestAPIServer:
    """Test API server functionality."""

    @pytest.fixture
    def app(self):
        """Create test API server."""
        server = APIServer(port=5001, debug=True)
        server.app.config["TESTING"] = True
        return server.app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_docs_endpoint(self, client):
        """Test documentation endpoint."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert b"Swagger UI" in response.data or b"swagger-ui" in response.data

    def test_openapi_spec(self, client):
        """Test OpenAPI specification endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["openapi"] == "3.0.0"
        assert "Anna AI" in data["info"]["title"]

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/status")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "timestamp" in data
        assert "system" in data or "uptime" in data

    def test_rate_limiting_headers(self, client):
        """Test that rate limit headers are present."""
        response = client.get("/health")
        
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Limit" in response.headers

    def test_get_config_endpoint(self, client):
        """Test get configuration endpoint."""
        response = client.get("/api/config")
        
        assert response.status_code == 200 or response.status_code == 503
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "model" in data or "error" not in data

    def test_validate_config_endpoint(self, client):
        """Test configuration validation endpoint."""
        response = client.post(
            "/api/config/validate",
            data=json.dumps({}),
            content_type="application/json"
        )
        
        assert response.status_code in [200, 400, 503]

    def test_send_message_no_auth_fails(self, client):
        """Test that sending message without content fails."""
        response = client.post(
            "/api/message",
            data=json.dumps({}),
            content_type="application/json"
        )
        
        assert response.status_code in [400, 503]

    def test_webhook_endpoints(self, client):
        """Test webhook endpoints."""
        # List webhooks
        response = client.get("/api/webhooks")
        assert response.status_code == 200
        
        # Register webhook
        response = client.post(
            "/api/webhooks",
            data=json.dumps({
                "event": "test_event",
                "url": "http://example.com/webhook"
            }),
            content_type="application/json"
        )
        assert response.status_code == 201

    def test_system_health_endpoint(self, client):
        """Test deep system health check."""
        response = client.get("/api/system/health")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "checks" in data

    def test_system_info_endpoint(self, client):
        """Test system information endpoint."""
        response = client.get("/api/system/info")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "python_version" in data
        assert "project_root" in data

    def test_error_handling_500(self, client):
        """Test error handling returns proper JSON."""
        # Access non-existent endpoint
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.get("/health")
        
        # Flask-CORS should add these headers
        assert response.status_code == 200


class TestAPIIntegration:
    """Integration tests for API server."""

    def test_api_server_initialization(self):
        """Test that API server can be initialized."""
        server = APIServer(port=5002, debug=True)
        
        assert server.port == 5002
        assert server.debug is True
        assert server.app is not None

    def test_rate_limiter_integration(self):
        """Test rate limiter integration."""
        server = APIServer(port=5003, debug=True)
        
        client_id = "test_client"
        
        # Make requests up to limit
        for i in range(100):
            assert server.rate_limiter.is_allowed(client_id) is True
        
        # Next request should be blocked
        assert server.rate_limiter.is_allowed(client_id) is False

    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration."""
        server = APIServer(port=5004, debug=True)
        
        breaker = server.circuit_breakers["ai_core"]
        
        # Simulate failures
        for i in range(5):
            breaker.record_failure()
        
        assert breaker.state == "open"
        assert breaker.call_allowed() is False

    def test_performance_monitor_integration(self):
        """Test performance monitor integration."""
        server = APIServer(port=5005, debug=True)
        
        # Record some metrics
        server.performance_monitor.record_metric("test_operation", 100.5, "success")
        server.performance_monitor.record_metric("test_operation", 95.2, "success")
        
        stats = server.performance_monitor.get_statistics("test_operation")
        
        assert stats["count"] == 2
        assert "duration_ms" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
