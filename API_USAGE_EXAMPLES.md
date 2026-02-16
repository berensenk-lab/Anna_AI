# Anna AI REST API - Usage Examples

Complete examples for using the Anna AI REST API.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Python Examples](#python-examples)
3. [JavaScript/Node Examples](#javascriptnodejs-examples)
4. [cURL Examples](#curl-examples)
5. [Advanced Usage](#advanced-usage)

---

## Basic Usage

### Starting the API Server

```bash
# Default port 5000
python api_server.py

# Custom port
python api_server.py --port 8000

# Debug mode
python api_server.py --debug
```

### API Documentation

- **Interactive Docs**: http://localhost:5000/docs
- **OpenAPI Spec**: http://localhost:5000/openapi.json
- **Home Page**: http://localhost:5000/

---

## Python Examples

### 1. Health Check

```python
import requests

response = requests.get("http://localhost:5000/health")
print(response.json())
# Output: {"status": "healthy", "timestamp": "2024-01-17T..."}
```

### 2. Get System Status

```python
import requests

response = requests.get("http://localhost:5000/status")
data = response.json()

print(f"Status: {data['status']}")
print(f"AI Core Ready: {data['ai_core_ready']}")
print(f"Uptime: {data['uptime_formatted']}")
print(f"CPU: {data['cpu_percent']}%")
print(f"Memory: {data['memory_mb']}MB")
```

### 3. Get Performance Metrics

```python
import requests
import json

response = requests.get("http://localhost:5000/metrics")
metrics = response.json()

print(json.dumps(metrics, indent=2))
```

### 4. Send Message to Agent

```python
import requests

response = requests.post(
    "http://localhost:5000/api/message",
    json={"message": "Hello Anna, how are you?"}
)

if response.status_code == 202:
    print("Message sent successfully")
else:
    print(f"Error: {response.json()}")
```

### 5. Get Configuration

```python
import requests

response = requests.get("http://localhost:5000/api/config")
config = response.json()

print(f"Model: {config['model']}")
print(f"Endpoint: {config['ollama_endpoint']}")
```

### 6. Update Configuration

```python
import requests

response = requests.post(
    "http://localhost:5000/api/config",
    json={
        "debug": True,
        "ollama_timeout": 120
    }
)

print(response.json())
```

### 7. Validate Configuration

```python
import requests

response = requests.post("http://localhost:5000/api/config/validate")
validation = response.json()

if validation['valid']:
    print("Configuration is valid")
else:
    print("Errors:", validation['errors'])
    print("Warnings:", validation['warnings'])
```

### 8. List Available Tools

```python
import requests

response = requests.get("http://localhost:5000/api/tools")
tools = response.json()

print("Available tools:")
for tool in tools['tools']:
    print(f"  - {tool}")
```

### 9. Execute Tool

```python
import requests

response = requests.post(
    "http://localhost:5000/api/tools/web_search/execute",
    json={"query": "python programming", "limit": 5}
)

if response.status_code == 200:
    result = response.json()
    print(f"Results: {result['result']}")
else:
    print(f"Error: {response.json()}")
```

### 10. Get Memory Statistics

```python
import requests

response = requests.get("http://localhost:5000/api/memory/stats")
stats = response.json()

print(f"Short-term memory: {stats['short_memory_entries']} entries")
print(f"Medium-term memory: {stats['medium_memory_entries']} entries")
print(f"Long-term memory: {stats['long_memory_summaries']} summaries")
```

### 11. System Health Check (Deep)

```python
import requests
import json

response = requests.get("http://localhost:5000/api/system/health")
health = response.json()

print(f"Overall Status: {health['status']}")
print(json.dumps(health['checks'], indent=2))
```

### 12. Register Webhook

```python
import requests

response = requests.post(
    "http://localhost:5000/api/webhooks",
    json={
        "event": "message_received",
        "url": "https://your-domain.com/webhook"
    }
)

if response.status_code == 201:
    webhook_id = response.json()['webhook_id']
    print(f"Webhook registered: {webhook_id}")
```

### 13. With API Key Authentication

```python
import requests

headers = {
    "X-API-Key": "your-api-key-here"
}

response = requests.get(
    "http://localhost:5000/api/config",
    headers=headers
)

print(response.json())
```

### 14. Complete Example: Async Message Processing

```python
import requests
import time
import json

def send_message_and_wait(message: str, max_wait: int = 10):
    """Send message and check for response."""
    
    # Send message
    response = requests.post(
        "http://localhost:5000/api/message",
        json={"message": message}
    )
    
    if response.status_code != 202:
        print(f"Error sending message: {response.json()}")
        return
    
    print(f"Message sent: {message}")
    
    # Wait for response
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:5000/api/response")
            data = response.json()
            
            if data.get("status") == "ready":
                print(f"Response: {data.get('message')}")
                return data.get('message')
            
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
    
    print("Timeout waiting for response")

# Usage
send_message_and_wait("What's the weather like?")
```

### 15. Client Class

```python
import requests
from typing import Dict, Any, Optional

class AnnaAIClient:
    """Client for Anna AI REST API."""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def health(self) -> Dict[str, Any]:
        """Check health."""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def status(self) -> Dict[str, Any]:
        """Get status."""
        response = self.session.get(f"{self.base_url}/status")
        return response.json()
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send message."""
        response = self.session.post(
            f"{self.base_url}/api/message",
            json={"message": message}
        )
        return response.json()
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration."""
        response = self.session.get(f"{self.base_url}/api/config")
        return response.json()
    
    def get_tools(self) -> list:
        """Get available tools."""
        response = self.session.get(f"{self.base_url}/api/tools")
        return response.json()["tools"]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute tool."""
        response = self.session.post(
            f"{self.base_url}/api/tools/{tool_name}/execute",
            json=kwargs
        )
        return response.json()
    
    def memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        response = self.session.get(f"{self.base_url}/api/memory/stats")
        return response.json()
    
    def system_health(self) -> Dict[str, Any]:
        """Get system health."""
        response = self.session.get(f"{self.base_url}/api/system/health")
        return response.json()

# Usage
client = AnnaAIClient()
print(client.health())
print(client.status())
tools = client.get_tools()
print(f"Available tools: {tools}")
```

---

## JavaScript/Node.js Examples

### 1. Basic Health Check

```javascript
fetch("http://localhost:5000/health")
    .then(response => response.json())
    .then(data => console.log(data));
```

### 2. Send Message (using axios)

```javascript
const axios = require('axios');

axios.post('http://localhost:5000/api/message', {
    message: 'Hello Anna!'
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### 3. Get Configuration

```javascript
fetch('http://localhost:5000/api/config')
    .then(r => r.json())
    .then(config => {
        console.log(`Model: ${config.model}`);
        console.log(`Endpoint: ${config.ollama_endpoint}`);
    });
```

### 4. Client Class

```javascript
class AnnaAIClient {
    constructor(baseUrl = 'http://localhost:5000', apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    async health() {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }

    async status() {
        const response = await fetch(`${this.baseUrl}/status`);
        return response.json();
    }

    async sendMessage(message) {
        const response = await fetch(`${this.baseUrl}/api/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(this.apiKey && { 'X-API-Key': this.apiKey })
            },
            body: JSON.stringify({ message })
        });
        return response.json();
    }

    async getConfig() {
        const response = await fetch(`${this.baseUrl}/api/config`);
        return response.json();
    }

    async getTools() {
        const response = await fetch(`${this.baseUrl}/api/tools`);
        const data = await response.json();
        return data.tools;
    }

    async executeTool(toolName, params) {
        const response = await fetch(`${this.baseUrl}/api/tools/${toolName}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(this.apiKey && { 'X-API-Key': this.apiKey })
            },
            body: JSON.stringify(params)
        });
        return response.json();
    }

    async getMemoryStats() {
        const response = await fetch(`${this.baseUrl}/api/memory/stats`);
        return response.json();
    }

    async getSystemHealth() {
        const response = await fetch(`${this.baseUrl}/api/system/health`);
        return response.json();
    }
}

// Usage
const client = new AnnaAIClient();
client.health().then(data => console.log(data));
```

---

## cURL Examples

### 1. Health Check

```bash
curl http://localhost:5000/health
```

### 2. Get Status

```bash
curl http://localhost:5000/status | jq .
```

### 3. Get Metrics

```bash
curl http://localhost:5000/metrics | jq '.system'
```

### 4. Send Message

```bash
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Anna"}'
```

### 5. Get Configuration

```bash
curl http://localhost:5000/api/config | jq .
```

### 6. Update Configuration

```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"debug": true}'
```

### 7. Validate Configuration

```bash
curl -X POST http://localhost:5000/api/config/validate | jq .
```

### 8. List Tools

```bash
curl http://localhost:5000/api/tools | jq .
```

### 9. Execute Tool

```bash
curl -X POST http://localhost:5000/api/tools/web_search/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "python"}'
```

### 10. Get Memory Stats

```bash
curl http://localhost:5000/api/memory/stats | jq .
```

### 11. System Health

```bash
curl http://localhost:5000/api/system/health | jq .
```

### 12. With API Key

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/config
```

### 13. With Rate Limit Headers

```bash
curl -i http://localhost:5000/health | grep X-RateLimit
```

### 14. Register Webhook

```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message_received",
    "url": "https://your-domain.com/webhook"
  }'
```

### 15. List Webhooks

```bash
curl http://localhost:5000/api/webhooks | jq .
```

---

## Advanced Usage

### 1. Monitoring Dashboard

```bash
# Monitor metrics every 5 seconds
watch -n 5 'curl -s http://localhost:5000/metrics | jq ".system"'
```

### 2. Testing Rate Limiting

```bash
# Make 105 requests (limit is 100)
for i in {1..105}; do
  curl -s http://localhost:5000/health > /dev/null
  if [ $? -ne 0 ]; then
    echo "Rate limited on request $i"
  fi
done
```

### 3. Webhook Testing

```bash
# Setup local webhook receiver (using ngrok or similar)
# Register webhook pointing to your receiver
# Trigger messages and observe webhook calls
```

### 4. Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:5000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:5000/health
```

### 5. Log Monitoring

```bash
# Monitor API logs in real-time
tail -f logs/api.json | jq '.message, .status_code'
```

---

## Error Handling

### Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted |
| 400 | Bad Request |
| 401 | Unauthorized |
| 429 | Rate Limited |
| 503 | Service Unavailable |

### Example Error Handling

```python
import requests

try:
    response = requests.get("http://localhost:5000/api/config")
    
    if response.status_code == 200:
        print(response.json())
    elif response.status_code == 401:
        print("Invalid API key")
    elif response.status_code == 429:
        print("Rate limited, retry after delay")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

except requests.exceptions.ConnectionError:
    print("Cannot connect to API server")
except requests.exceptions.Timeout:
    print("Request timeout")
```

---

## Best Practices

1. **Use API Keys** - Set `ANNA_API_KEYS` environment variable
2. **Monitor Rate Limits** - Check `X-RateLimit-Remaining` header
3. **Handle Timeouts** - Set appropriate timeout values
4. **Implement Retries** - Use exponential backoff for failures
5. **Monitor Webhooks** - Log webhook delivery status
6. **Cache Results** - Reduce API calls with intelligent caching
7. **Batch Operations** - Combine multiple operations when possible
8. **Monitor Logs** - Regularly check JSON logs for errors

---

**For more information, see:**
- DEPLOYMENT_GUIDE.md
- PHASE_2_SUMMARY.md
- Interactive Docs: http://localhost:5000/docs
