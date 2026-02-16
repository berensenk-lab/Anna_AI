# Phase 2 Quick Reference

## Phase 2 Implementation - Quick Start

### What Was Added

✅ **REST API Server** (`api_server.py`) - 15+ endpoints for remote control  
✅ **Configuration Validator** - Validates all config files  
✅ **Structured JSON Logging** - Log aggregation ready  
✅ **Performance Monitor** - Real-time metrics tracking  
✅ **Deployment Guide** - Complete deployment instructions  

### Start Using Phase 2

```bash
# Start API server
python api_server.py

# In another terminal, try endpoints
curl http://localhost:5000/health
curl http://localhost:5000/status
curl http://localhost:5000/metrics

# API documentation
open http://localhost:5000/
```

### New Make Commands

```bash
# API Server
make run-api              # Start API on port 5000
make run-api-port PORT=8000  # Custom port
make run-api-debug        # Debug mode

# Configuration
make validate-config      # Validate all configs
make generate-docs        # Generate API docs

# Monitoring
make monitor-performance  # View performance stats

# Docker
make docker-shell         # Enter container
make docker-stats         # View resource usage
```

### API Endpoints

**Health & Monitoring:**
```
GET  /health              Check server is running
GET  /status              Detailed system status
GET  /metrics             Performance metrics
```

**Configuration:**
```
GET  /api/config          Get current config
POST /api/config          Update configuration
```

**Agent Control:**
```
POST /api/message         Send message to agent
GET  /api/response        Get agent response
```

**Tools:**
```
GET  /api/tools           List available tools
POST /api/tools/<name>/execute    Execute tool
```

**Memory:**
```
GET  /api/memory/stats    Memory statistics
```

**System:**
```
GET  /api/system/info     System information
POST /api/system/shutdown Shutdown server
```

### Monitoring

**Real-time metrics:**
```bash
watch -n 1 'curl -s http://localhost:5000/metrics | jq .'
```

**View JSON logs:**
```bash
tail -f logs/app.json | jq .
tail -f logs/api.json | jq .
tail -f logs/errors.json | jq .
```

**Performance statistics:**
```bash
curl -s http://localhost:5000/metrics | jq '.duration_ms'
```

### Validation

**Validate configuration:**
```bash
python main.py --check
make validate-config
```

**Check all systems:**
```python
from BASE.config_validator import ConfigValidator
validator = ConfigValidator()
print(validator.generate_report())
```

### Deployment

**Local development:**
```bash
python main.py
python api_server.py
```

**Docker:**
```bash
docker compose up -d
docker compose logs -f
```

**Linux server:**
```bash
sudo systemctl start anna-ai
sudo journalctl -u anna-ai -f
```

See `DEPLOYMENT_GUIDE.md` for full instructions.

### Performance Tracking

```python
from BASE.performance_monitor import PerformanceMonitor, PerformanceTimer

monitor = PerformanceMonitor()

with PerformanceTimer("my_operation", monitor) as timer:
    # Do work
    pass

print(monitor.get_summary())
```

### JSON Logging

```python
from BASE.structured_logger import LogManager

log_manager = LogManager()
log_manager.log_api_request(
    method="POST",
    endpoint="/api/message",
    status_code=200,
    duration_ms=145.3
)
```

### File Locations

| Component | Location |
|-----------|----------|
| API Server | `api_server.py` |
| Config Validator | `BASE/config_validator.py` |
| JSON Logger | `BASE/structured_logger.py` |
| Performance Monitor | `BASE/performance_monitor.py` |
| Deployment Guide | `DEPLOYMENT_GUIDE.md` |
| App Logs | `logs/app.json` |
| API Logs | `logs/api.json` |
| Error Logs | `logs/errors.json` |

### Configuration Validation

**What gets validated:**
- `.env` file format
- `config.json` structure
- Environment variables
- Required directories
- Model availability
- Breaking changes

**Run validation:**
```bash
python -c "from BASE.config_validator import ConfigValidator; \
    print(ConfigValidator().generate_report())"
```

### Troubleshooting

**API server won't start?**
```bash
python api_server.py --debug
```

**Check logs:**
```bash
tail -f logs/errors.json | jq .
```

**Port already in use?**
```bash
python api_server.py --port 8000
```

**Configuration issues?**
```bash
make validate-config
```

### Testing Phase 2

```bash
# Test API endpoints
curl -s http://localhost:5000/health | jq .
curl -s http://localhost:5000/status | jq .

# Validate configuration
python main.py --check

# Check performance
curl -s http://localhost:5000/metrics | jq .

# View logs
cat logs/app.json | jq '.level, .message'
```

### Dependencies Added

```
flask==3.0.0           # REST API
flask-cors==4.0.0      # CORS support
psutil==5.9.6          # System monitoring
python-json-logger==2.0.7  # JSON logging
```

Install with:
```bash
pip install -r requirements.txt
```

### Next Steps

1. ✅ Start API server: `python api_server.py`
2. ✅ Visit documentation: http://localhost:5000/
3. ✅ Validate configuration: `make validate-config`
4. ✅ Review deployment guide: `DEPLOYMENT_GUIDE.md`
5. ✅ Monitor performance: `curl http://localhost:5000/metrics`

### Resources

- **API Documentation**: http://localhost:5000/
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Phase 2 Summary**: `PHASE_2_SUMMARY.md`
- **GitHub**: https://github.com/KryptykBioz/Anna_AI
- **Configuration Schema**: `BASE/config_validator.py`

---

**Phase 2 Status**: Complete ✓  
**Phase 1 Status**: Completed ✓  
**Ready for Production**: Yes ✓  
**Next Phase**: Phase 3 (Advanced Features)

**Quick Start Summary:**
- API: `python api_server.py` → http://localhost:5000/
- Main: `python main.py` → GUI or CLI
- Tests: `pytest -v`
- Logs: `tail -f logs/*.json`
- Deploy: See `DEPLOYMENT_GUIDE.md`
