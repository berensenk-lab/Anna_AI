"""
Enhanced REST API Server for Anna AI - Phase 2 Complete

Provides HTTP endpoints with:
- Structured JSON logging
- API authentication via API keys
- Rate limiting
- Real performance metrics
- OpenAPI/Swagger documentation
- Error recovery and circuit breaker
- Webhook support

Usage:
    python api_server.py                 # Start on default port
    python api_server.py --port 8000     # Custom port
    python api_server.py --debug         # Debug mode
"""

import os
import sys
import argparse
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
import psutil
import json

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from BASE.core.config import Config
from BASE.core.logger import Logger, MessageType
from BASE.core.core_initializer import CoreInitializer
from BASE.structured_logger import LogManager
from BASE.performance_monitor import PerformanceMonitor, PerformanceTimer
from BASE.config_validator import ConfigValidator


class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.

        Args:
            client_id: Client identifier (IP address, API key, etc.)

        Returns:
            True if allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds

            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff
            ]

            # Check limit
            if len(self.requests[client_id]) >= self.max_requests:
                return False

            # Add new request
            self.requests[client_id].append(now)
            return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            valid_requests = len([
                req_time for req_time in self.requests.get(client_id, [])
                if req_time > cutoff
            ])
            return max(0, self.max_requests - valid_requests)


class CircuitBreaker:
    """Circuit breaker for managing service failures."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self.lock = threading.Lock()

    def record_success(self) -> None:
        """Record successful call."""
        with self.lock:
            self.failures = 0
            self.state = "closed"

    def record_failure(self) -> None:
        """Record failed call."""
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = "open"

    def call_allowed(self) -> bool:
        """Check if call is allowed."""
        with self.lock:
            if self.state == "closed":
                return True

            if self.state == "open":
                if self.last_failure_time and \
                   time.time() - self.last_failure_time > self.timeout_seconds:
                    self.state = "half-open"
                    return True
                return False

            # half-open
            return True


class APIServer:
    """Enhanced REST API server for Anna AI."""

    def __init__(self, port: int = 5000, debug: bool = False):
        """
        Initialize API server.

        Args:
            port: Server port
            debug: Enable debug mode
        """
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self.config: Optional[Config] = None
        self.logger: Optional[Logger] = None
        # Initialize structured logging at construction time so request hooks
        # and error handlers are safe before explicit server initialization.
        self.log_manager: Optional[LogManager] = LogManager()
        self.ai_core = None
        self.start_time = datetime.now()

        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor()

        # Initialize rate limiting
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

        # Initialize circuit breakers
        self.circuit_breakers = {
            "ai_core": CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            "memory": CircuitBreaker(failure_threshold=3, timeout_seconds=30),
        }

        # API keys for authentication
        self.valid_api_keys = set(os.getenv("ANNA_API_KEYS", "").split(",")) if os.getenv("ANNA_API_KEYS") else set()

        # Webhooks registry
        self.webhooks: Dict[str, list] = defaultdict(list)

        # Setup CORS
        CORS(self.app)

        # Setup routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Register all API routes."""
        # Documentation routes
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/docs", "docs", self.docs)
        self.app.add_url_rule("/openapi.json", "openapi", self.openapi_spec)

        # Health and status routes
        self.app.add_url_rule("/health", "health", self.health, methods=["GET"])
        self.app.add_url_rule("/status", "status", self.status, methods=["GET"])
        self.app.add_url_rule("/metrics", "metrics", self.metrics, methods=["GET"])

        # Configuration routes
        self.app.add_url_rule("/api/config", "get_config", self.get_config, methods=["GET"])
        self.app.add_url_rule("/api/config", "set_config", self.set_config, methods=["POST", "PUT"])
        self.app.add_url_rule("/api/config/validate", "validate_config", self.validate_config, methods=["POST"])

        # Agent interaction routes
        self.app.add_url_rule("/api/message", "send_message", self.send_message, methods=["POST"])
        self.app.add_url_rule("/api/response", "get_response", self.get_response, methods=["GET"])

        # Tool routes
        self.app.add_url_rule("/api/tools", "list_tools", self.list_tools, methods=["GET"])
        self.app.add_url_rule("/api/tools/<tool_name>/execute", "execute_tool", self.execute_tool, methods=["POST"])

        # Memory routes
        self.app.add_url_rule("/api/memory/stats", "memory_stats", self.memory_stats, methods=["GET"])

        # System routes
        self.app.add_url_rule("/api/system/info", "system_info", self.system_info, methods=["GET"])
        self.app.add_url_rule("/api/system/health", "system_health", self.system_health, methods=["GET"])
        self.app.add_url_rule("/api/system/shutdown", "system_shutdown", self.system_shutdown, methods=["POST"])

        # Webhook routes
        self.app.add_url_rule("/api/webhooks", "list_webhooks", self.list_webhooks, methods=["GET"])
        self.app.add_url_rule("/api/webhooks", "register_webhook", self.register_webhook, methods=["POST"])
        self.app.add_url_rule("/api/webhooks/<webhook_id>", "unregister_webhook", self.unregister_webhook, methods=["DELETE"])

        # Error handlers
        self.app.register_error_handler(HTTPException, self.handle_http_error)
        self.app.register_error_handler(Exception, self.handle_exception)

        # Before request
        self.app.before_request(self._before_request)

        # After request
        self.app.after_request(self._after_request)

    def _before_request(self) -> Optional[tuple]:
        """Called before each request."""
        # Skip authentication for public endpoints
        public_endpoints = ["/", "/docs", "/health", "/openapi.json"]

        if request.path not in public_endpoints:
            # Check API key authentication
            api_key = request.headers.get("X-API-Key")

            if self.valid_api_keys and api_key not in self.valid_api_keys:
                return jsonify({"error": "Invalid or missing API key"}), 401

        # Check rate limiting
        client_id = request.remote_addr or "unknown"

        if not self.rate_limiter.is_allowed(client_id):
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Store request start time for metrics
        request.start_time = time.time()

    def _after_request(self, response):
        """Called after each request."""
        if hasattr(request, "start_time"):
            duration_ms = (time.time() - request.start_time) * 1000

            # Log API request
            self.log_manager.log_api_request(
                method=request.method,
                endpoint=request.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=request.remote_addr,
            )

            # Record metric
            metric_name = f"{request.method} {request.path}"
            self.performance_monitor.record_metric(
                name=metric_name,
                duration_ms=duration_ms,
                status="success" if response.status_code < 400 else "failed",
            )

        # Add rate limit headers
        client_id = request.remote_addr or "unknown"
        remaining = self.rate_limiter.get_remaining(client_id)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = "100"

        return response

    def _check_api_key(self) -> Optional[tuple]:
        """Check if request has valid API key."""
        if not self.valid_api_keys:
            return None

        api_key = request.headers.get("X-API-Key")

        if api_key not in self.valid_api_keys:
            return jsonify({"error": "Invalid API key"}), 401

        return None

    def initialize(self) -> bool:
        """
        Initialize the API server with AI core.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print("[INFO] Initializing API server components...")

            # Initialize config and logger
            self.config = Config()
            self.logger = Logger(self.config)

            # Initialize AI core
            core_initializer = CoreInitializer(self.config, self.logger)
            self.ai_core = core_initializer.initialize()

            if not self.ai_core:
                print("[ERROR] Failed to initialize AI core")
                self.log_manager.log_event("api", "Failed to initialize AI core", "ERROR")
                return False

            self.log_manager.log_event("api", "API server initialized successfully", "INFO")
            print(f"[INFO] API server ready on port {self.port}")
            return True

        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========== Utility Methods ==========

    def _get_uptime(self) -> Dict[str, Any]:
        """Get server uptime information."""
        uptime = datetime.now() - self.start_time
        return {
            "started_at": self.start_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split(".")[0],
        }

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics."""
        try:
            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "system_cpu_percent": psutil.cpu_percent(interval=0.1),
                "system_memory_percent": psutil.virtual_memory().percent,
            }
        except Exception as e:
            return {"error": str(e)}

    def _trigger_webhooks(self, event_type: str, data: Dict[str, Any]) -> None:
        """Trigger webhooks for an event."""
        if event_type not in self.webhooks:
            return

        for webhook in self.webhooks[event_type]:
            try:
                # Send webhook asynchronously
                def send_webhook():
                    import requests
                    try:
                        requests.post(
                            webhook["url"],
                            json={"event": event_type, "data": data},
                            headers={"Content-Type": "application/json"},
                            timeout=5,
                        )
                    except Exception as e:
                        self.log_manager.log_event(
                            "webhooks",
                            f"Webhook delivery failed: {e}",
                            "WARNING",
                        )

                thread = threading.Thread(target=send_webhook, daemon=True)
                thread.start()

            except Exception as e:
                self.log_manager.log_event("webhooks", f"Webhook error: {e}", "ERROR")

    # ========== Route Handlers ==========

    def index(self) -> str:
        """Serve API documentation."""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Anna AI - REST API</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
                header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; margin: -40px -20px 40px -20px; }
                h1 { margin-bottom: 10px; }
                .subtitle { opacity: 0.9; }
                .section { background: white; padding: 30px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .endpoint { background: #f9f9f9; padding: 20px; margin: 15px 0; border-left: 4px solid #667eea; border-radius: 4px; }
                .method { font-weight: bold; color: white; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-right: 10px; }
                .method.GET { background: #61affe; }
                .method.POST { background: #49cc90; }
                .method.PUT { background: #fca130; }
                .method.DELETE { background: #f93e3e; }
                code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
                .links { display: flex; gap: 20px; margin-top: 20px; }
                .links a { display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }
                .links a:hover { background: #764ba2; }
            </style>
        </head>
        <body>
            <header>
                <div class="container">
                    <h1>Anna AI - REST API</h1>
                    <p class="subtitle">Advanced AI Agent Control and Monitoring</p>
                </div>
            </header>
            <div class="container">
                <div class="section">
                    <h2>Welcome</h2>
                    <p>Anna AI REST API is running and ready for requests. Choose a documentation option:</p>
                    <div class="links">
                        <a href="/docs">Interactive Docs (Swagger UI)</a>
                        <a href="/openapi.json">OpenAPI Specification</a>
                    </div>
                </div>

                <div class="section">
                    <h2>Quick Start</h2>
                    <div class="endpoint">
                        <span class="method GET">GET</span> <code>/health</code>
                        <p>Check server health</p>
                    </div>
                    <div class="endpoint">
                        <span class="method GET">GET</span> <code>/status</code>
                        <p>Get detailed status information</p>
                    </div>
                    <div class="endpoint">
                        <span class="method POST">POST</span> <code>/api/message</code>
                        <p>Send message to Anna AI</p>
                    </div>
                </div>

                <div class="section">
                    <h2>Authentication</h2>
                    <p>Provide your API key in the <code>X-API-Key</code> header:</p>
                    <pre>curl -H "X-API-Key: your-api-key" http://localhost:5000/api/config</pre>
                </div>

                <div class="section">
                    <h2>Rate Limiting</h2>
                    <p>API is rate limited to 100 requests per 60 seconds.</p>
                    <p>Check the <code>X-RateLimit-Remaining</code> header in responses.</p>
                </div>
            </div>
        </body>
        </html>
        """)

    def docs(self) -> str:
        """Serve Swagger UI documentation."""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Anna AI - API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css">
            <style>
                html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
                *, *:before, *:after { box-sizing: inherit; }
                body { margin: 0; padding: 0; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js"></script>
            <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout"
                })
            }
            </script>
        </body>
        </html>
        """)

    def openapi_spec(self) -> Dict[str, Any]:
        """Return OpenAPI specification."""
        return jsonify({
            "openapi": "3.0.0",
            "info": {
                "title": "Anna AI REST API",
                "description": "Advanced AI agent control and monitoring API",
                "version": "2.0.0",
                "contact": {
                    "name": "KryptykBioz",
                    "url": "https://github.com/KryptykBioz/Anna_AI",
                }
            },
            "servers": [
                {"url": f"http://localhost:{self.port}", "description": "Local server"}
            ],
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "tags": ["Health"],
                        "responses": {
                            "200": {
                                "description": "Server is healthy",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "timestamp": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/status": {
                    "get": {
                        "summary": "Detailed Status",
                        "tags": ["Status"],
                        "responses": {
                            "200": {
                                "description": "Detailed system status"
                            }
                        }
                    }
                },
                "/metrics": {
                    "get": {
                        "summary": "Performance Metrics",
                        "tags": ["Monitoring"],
                        "responses": {
                            "200": {
                                "description": "Performance metrics"
                            }
                        }
                    }
                },
                "/api/config": {
                    "get": {
                        "summary": "Get Configuration",
                        "tags": ["Configuration"],
                        "responses": {
                            "200": {"description": "Current configuration"}
                        }
                    },
                    "post": {
                        "summary": "Update Configuration",
                        "tags": ["Configuration"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Configuration updated"}
                        }
                    }
                },
                "/api/message": {
                    "post": {
                        "summary": "Send Message to Agent",
                        "tags": ["Agent"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        },
                                        "required": ["message"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "202": {"description": "Message sent"}
                        }
                    }
                }
            }
        })

    def health(self) -> tuple:
        """Health check endpoint."""
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

    def status(self) -> tuple:
        """Detailed status endpoint."""
        return jsonify(
            {
                "status": "running",
                "ai_core_ready": self.ai_core is not None,
                "timestamp": datetime.now().isoformat(),
                **self._get_uptime(),
                **self._get_system_stats(),
            }
        ), 200

    def metrics(self) -> tuple:
        """Performance metrics endpoint with real data."""
        stats = self.performance_monitor.get_summary()
        
        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "system": self._get_system_stats(),
                "uptime": self._get_uptime(),
                "performance": stats,
            }
        ), 200

    def get_config(self) -> tuple:
        """Get current configuration."""
        if not self.config:
            return jsonify({"error": "Configuration not available"}), 503

        config_data = {
            "model": getattr(self.config, "MODEL", "unknown"),
            "thinking_model": getattr(self.config, "THINKING_MODEL", "unknown"),
            "embedding_model": getattr(self.config, "EMBEDDING_MODEL", "unknown"),
            "ollama_endpoint": os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
            "debug": self.config.DEBUG if hasattr(self.config, "DEBUG") else False,
        }

        return jsonify(config_data), 200

    def set_config(self) -> tuple:
        """Update configuration."""
        if not self.config:
            return jsonify({"error": "Configuration not available"}), 503

        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            changes = {}
            for key, value in data.items():
                if hasattr(self.config, key.upper()):
                    setattr(self.config, key.upper(), value)
                    changes[key] = value

            self.log_manager.log_event("api", f"Configuration updated: {changes}", "INFO")
            return jsonify({"status": "updated", "changes": changes}), 200

        except Exception as e:
            self.log_manager.log_event("api", f"Config update failed: {e}", "ERROR")
            return jsonify({"error": str(e)}), 400

    def validate_config(self) -> tuple:
        """Validate configuration."""
        try:
            validator = ConfigValidator()
            is_valid, errors, warnings = validator.validate_all()

            report = {
                "valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "timestamp": datetime.now().isoformat(),
            }

            self.log_manager.log_event("api", "Configuration validation performed", "INFO")
            return jsonify(report), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def send_message(self) -> tuple:
        """Send message to agent."""
        if not self.ai_core:
            self.circuit_breakers["ai_core"].record_failure()
            return jsonify({"error": "AI core not ready"}), 503

        try:
            data = request.get_json()

            if not data or "message" not in data:
                return jsonify({"error": "No message provided"}), 400

            message = data["message"]

            with PerformanceTimer("send_message", self.performance_monitor) as timer:
                self.ai_core.process_user_message(message)

            self.circuit_breakers["ai_core"].record_success()
            self._trigger_webhooks("message_received", {"message": message})

            return jsonify({"status": "sent", "message": message}), 202

        except Exception as e:
            self.circuit_breakers["ai_core"].record_failure()
            self.log_manager.log_event("api", f"Message send failed: {e}", "ERROR")
            return jsonify({"error": str(e)}), 400

    def get_response(self) -> tuple:
        """Get agent response."""
        if not self.ai_core:
            return jsonify({"error": "AI core not ready"}), 503

        try:
            response = {
                "status": "pending",
                "message": "Check cognitive loop output for responses",
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def list_tools(self) -> tuple:
        """List available tools."""
        if not self.ai_core or not hasattr(self.ai_core, "tool_manager"):
            return jsonify({"error": "Tool manager not available"}), 503

        try:
            tools = self.ai_core.tool_manager.get_enabled_tool_names()
            return jsonify({"tools": tools}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def execute_tool(self, tool_name: str) -> tuple:
        """Execute a specific tool."""
        if not self.ai_core or not hasattr(self.ai_core, "tool_manager"):
            self.circuit_breakers["ai_core"].record_failure()
            return jsonify({"error": "Tool manager not available"}), 503

        try:
            data = request.get_json() or {}

            with PerformanceTimer(f"tool_{tool_name}", self.performance_monitor) as timer:
                result = self.ai_core.tool_manager.execute_tool(tool_name, data)

            self.circuit_breakers["ai_core"].record_success()
            self.log_manager.log_tool_execution(
                tool_name=tool_name,
                command=data.get("command", "execute"),
                status="success",
                duration_ms=timer.duration_ms,
            )

            return jsonify({"status": "executed", "result": result}), 200

        except Exception as e:
            self.circuit_breakers["ai_core"].record_failure()
            self.log_manager.log_event("api", f"Tool execution failed: {e}", "ERROR")
            return jsonify({"error": str(e)}), 400

    def memory_stats(self) -> tuple:
        """Get memory statistics."""
        if not self.ai_core:
            self.circuit_breakers["memory"].record_failure()
            return jsonify({"error": "AI core not ready"}), 503

        try:
            memory_manager = self.ai_core.get_memory_manager()
            stats = memory_manager.get_stats()

            self.circuit_breakers["memory"].record_success()
            self.log_manager.log_memory_operation(
                operation="stats",
                tier="all",
                size=stats.get("short_memory_entries", 0),
                duration_ms=0,
            )

            return jsonify(stats), 200

        except Exception as e:
            self.circuit_breakers["memory"].record_failure()
            self.log_manager.log_event("api", f"Memory stats failed: {e}", "ERROR")
            return jsonify({"error": str(e)}), 400

    def system_info(self) -> tuple:
        """Get comprehensive system information."""
        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "python_version": sys.version,
                "project_root": str(PROJECT_ROOT),
                **self._get_system_stats(),
                **self._get_uptime(),
            }
        ), 200

    def system_health(self) -> tuple:
        """Deep system health check."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {
                "ai_core": {
                    "status": "ok" if self.ai_core else "error",
                    "circuit_breaker": self.circuit_breakers["ai_core"].state,
                },
                "memory": {
                    "status": "ok",
                    "circuit_breaker": self.circuit_breakers["memory"].state,
                },
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                },
            },
        }

        # Overall status
        if any(check.get("status") == "error" for check in health["checks"].values()):
            health["status"] = "degraded"

        return jsonify(health), 200

    def system_shutdown(self) -> tuple:
        """Shutdown the API server."""
        try:
            self.log_manager.log_event("api", "System shutdown initiated", "INFO")

            if self.ai_core and hasattr(self.ai_core, "shutdown"):
                self.ai_core.shutdown()

            def shutdown_server():
                time.sleep(1)
                sys.exit(0)

            threading.Thread(target=shutdown_server, daemon=True).start()

            return jsonify({"status": "shutting_down"}), 202

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def list_webhooks(self) -> tuple:
        """List registered webhooks."""
        webhooks_list = []
        for event_type, webhooks in self.webhooks.items():
            for idx, webhook in enumerate(webhooks):
                webhooks_list.append({
                    "id": f"{event_type}_{idx}",
                    "event": event_type,
                    "url": webhook["url"],
                })

        return jsonify({"webhooks": webhooks_list}), 200

    def register_webhook(self) -> tuple:
        """Register a webhook."""
        try:
            data = request.get_json()

            if not data or "url" not in data or "event" not in data:
                return jsonify({"error": "Missing url or event"}), 400

            event = data["event"]
            url = data["url"]

            self.webhooks[event].append({"url": url})

            webhook_id = f"{event}_{len(self.webhooks[event]) - 1}"

            self.log_manager.log_event("webhooks", f"Webhook registered: {webhook_id}", "INFO")

            return jsonify({"status": "registered", "webhook_id": webhook_id}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def unregister_webhook(self, webhook_id: str) -> tuple:
        """Unregister a webhook."""
        try:
            for event_type, webhooks in list(self.webhooks.items()):
                self.webhooks[event_type] = [
                    w for w in webhooks
                    if f"{event_type}_{webhooks.index(w)}" != webhook_id
                ]

            self.log_manager.log_event("webhooks", f"Webhook unregistered: {webhook_id}", "INFO")

            return jsonify({"status": "unregistered"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # ========== Error Handlers ==========

    def handle_http_error(self, e: HTTPException) -> tuple:
        """Handle HTTP exceptions."""
        self.log_manager.log_event("api", f"HTTP error: {e.name}", "WARNING")

        return (
            jsonify({"error": e.name, "description": e.description}),
            e.code,
        )

    def handle_exception(self, e: Exception) -> tuple:
        """Handle unexpected exceptions."""
        self.log_manager.log_event("api", f"Unexpected error: {e}", "ERROR")

        return (
            jsonify({"error": "Internal server error", "message": str(e)}),
            500,
        )

    def run(self) -> None:
        """Start the API server."""
        try:
            print(f"[INFO] Starting Anna AI API Server on port {self.port}...")
            print(f"[INFO] API Documentation: http://localhost:{self.port}/")
            print(f"[INFO] Swagger UI: http://localhost:{self.port}/docs")
            self.app.run(
                host="0.0.0.0",
                port=self.port,
                debug=self.debug,
                use_reloader=False,
            )

        except Exception as e:
            print(f"[ERROR] Server failed: {e}")
            import traceback
            traceback.print_exc()


def main() -> int:
    """Main entry point for API server."""
    parser = argparse.ArgumentParser(
        description="Anna AI REST API Server - Phase 2 Complete",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_server.py                # Start on default port 5000
  python api_server.py --port 8000   # Custom port
  python api_server.py --debug       # Debug mode
        """,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Server port (default: 5000)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Anna AI API Server 2.0.0",
    )

    args = parser.parse_args()

    # Create and initialize server
    server = APIServer(port=args.port, debug=args.debug)

    if not server.initialize():
        print("[ERROR] Failed to initialize API server")
        return 1

    # Run server
    try:
        server.run()
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
