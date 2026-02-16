# Deployment Guide for Anna AI

This guide covers deploying Anna AI in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Linux Server Deployment](#linux-server-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Checklist](#production-checklist)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Local Development

### Prerequisites

- Python 3.11+
- pip or poetry
- Ollama (for LLM)

### Installation

```bash
# Clone repository
git clone https://github.com/KryptykBioz/Anna_AI.git
cd Anna_AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install transformers==4.38.2

# For GPU support (RTX 50-series)
# Copy GPU packages from working Anna_AI instance
# See SETUP.md for detailed GPU setup
```

### Running the Application

```bash
# GUI mode (default)
python main.py

# CLI mode
python main.py --no-gui

# Health check
python main.py --check

# Verbose logging
python main.py -v

# API server
python api_server.py

# API server on custom port
python api_server.py --port 8000
```

### Development Workflow

```bash
# Install dev tools
make install-dev

# Run tests
make test

# Code formatting and linting
make format
make lint

# Generate coverage report
pytest --cov=BASE --cov-report=html
```

---

## Docker Deployment

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (for compose deployments)

### Quick Start

```bash
# Build image
docker build -t anna-ai:latest .

# Run with compose (includes Ollama)
docker compose up -d

# View logs
docker compose logs -f anna-ai

# Stop services
docker compose down
```

### Docker Compose Services

The `docker-compose.yml` includes:

1. **Ollama** - LLM inference engine
   - Port: 11434
   - Data persisted in `ollama_data` volume

2. **Anna-ai** - Main application
   - Port: 5000 (API server)
   - Volumes: `personality/`, `models/`, `logs/`

3. **Redis** (Optional)
   - Port: 6379
   - For caching and future enhancements
   - Profile: `optional`

### Running Optional Services

```bash
# Include Redis for caching
docker compose --profile optional up -d

# View all services
docker compose ps

# Check service health
docker compose ps
```

### Scaling Docker Deployment

```bash
# Run multiple replicas with load balancing
docker compose up -d --scale anna-ai=3

# Use environment variables for configuration
export OLLAMA_ENDPOINT=http://ollama:11434
export LOG_LEVEL=DEBUG
docker compose up -d
```

---

## Linux Server Deployment

### System Requirements

- Ubuntu 20.04+ or similar Linux distribution
- 4GB RAM minimum (8GB+ recommended)
- 50GB disk space minimum
- NVIDIA GPU (optional, for acceleration)

### Installation

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  git \
  curl \
  libsndfile1 \
  portaudio19-dev \
  ffmpeg

# Clone repository
git clone https://github.com/KryptykBioz/Anna_AI.git
cd Anna_AI

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install transformers==4.38.2
```

### Systemd Service (Auto-start)

Create `/etc/systemd/system/anna-ai.service`:

```ini
[Unit]
Description=Anna AI Agentic System
After=network.target

[Service]
Type=simple
User=anna
WorkingDirectory=/home/anna/Anna_AI
Environment="PATH=/home/anna/Anna_AI/venv/bin"
ExecStart=/home/anna/Anna_AI/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Create anna user
sudo useradd -m -d /home/anna anna

# Set permissions
sudo chown -R anna:anna /home/anna/Anna_AI

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable anna-ai
sudo systemctl start anna-ai

# Check status
sudo systemctl status anna-ai

# View logs
sudo journalctl -u anna-ai -f
```

### API Server Service

Create `/etc/systemd/system/anna-api.service`:

```ini
[Unit]
Description=Anna AI API Server
After=network.target anna-ai.service

[Service]
Type=simple
User=anna
WorkingDirectory=/home/anna/Anna_AI
Environment="PATH=/home/anna/Anna_AI/venv/bin"
ExecStart=/home/anna/Anna_AI/venv/bin/python api_server.py --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable anna-api
sudo systemctl start anna-api
```

### Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt-get install -y nginx
```

Configure `/etc/nginx/sites-available/anna-ai`:

```nginx
upstream anna_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name anna-ai.example.com;

    location / {
        proxy_pass http://anna_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/anna-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.large or larger
   - Storage: 50GB+ EBS volume

2. **Security Group**
   - SSH (22): Your IP only
   - HTTP (80): Public
   - HTTPS (443): Public
   - API (8000): Public or restricted

3. **Install & Run**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow Linux Server Deployment steps
```

### Google Cloud Run (Containerized)

```bash
# Build image for Cloud Run
docker build -t gcr.io/your-project/anna-ai:latest .

# Push to Container Registry
docker push gcr.io/your-project/anna-ai:latest

# Deploy
gcloud run deploy anna-ai \
  --image gcr.io/your-project/anna-ai:latest \
  --platform managed \
  --region us-central1 \
  --port 5000
```

### Azure Container Instances

```bash
# Push to Azure Container Registry
az acr build --registry your-registry \
  --image anna-ai:latest .

# Deploy
az container create \
  --resource-group your-group \
  --name anna-ai \
  --image your-registry.azurecr.io/anna-ai:latest \
  --ports 5000 80
```

### Kubernetes (Multi-container orchestration)

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anna-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: anna-ai
  template:
    metadata:
      labels:
        app: anna-ai
    spec:
      containers:
      - name: anna-ai
        image: anna-ai:latest
        ports:
        - containerPort: 5000
        env:
        - name: OLLAMA_ENDPOINT
          value: "http://ollama:11434"
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: anna-ai-service
spec:
  type: LoadBalancer
  selector:
    app: anna-ai
  ports:
  - port: 80
    targetPort: 5000
```

Deploy:

```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs -f deployment/anna-ai
```

---

## Production Checklist

### Security

- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure authentication for API
- [ ] Rotate API keys regularly
- [ ] Enable audit logging
- [ ] Set up DDoS protection
- [ ] Use secure environment variables
- [ ] Disable debug mode

### Performance

- [ ] Enable caching (Redis)
- [ ] Set up load balancing
- [ ] Configure resource limits
- [ ] Enable compression
- [ ] Optimize database queries
- [ ] Monitor performance metrics

### Monitoring

- [ ] Set up application monitoring
- [ ] Configure log aggregation
- [ ] Create alerting rules
- [ ] Set up uptime monitoring
- [ ] Track error rates
- [ ] Monitor resource usage

### Backup & Recovery

- [ ] Enable memory backups (daily)
- [ ] Set up disaster recovery
- [ ] Test recovery procedures
- [ ] Document runbooks
- [ ] Version control configurations

### Updates & Maintenance

- [ ] Plan update schedule
- [ ] Test updates in staging
- [ ] Document breaking changes
- [ ] Maintain changelog
- [ ] Security patch schedule

---

## Monitoring and Maintenance

### Health Check Endpoint

```bash
# Check server health
curl http://localhost:5000/health

# Get detailed status
curl http://localhost:5000/status

# View metrics
curl http://localhost:5000/metrics
```

### Configuration Validation

```bash
# Validate configuration
python main.py --check

# Verbose validation
python main.py -v --check
```

### Log Analysis

```bash
# View application logs
tail -f logs/app.json

# View API logs
tail -f logs/api.json

# View error logs
tail -f logs/errors.json

# Parse JSON logs
cat logs/app.json | jq .
```

### Performance Monitoring

```bash
# Monitor system resources
watch -n 1 'ps aux | grep python | grep -v grep'

# Check memory usage
top -p $(pgrep -f 'python main.py')

# Monitor network connections
netstat -an | grep LISTEN
```

### Backup Memory

```bash
# Backup personality/memory directory
tar -czf anna_memory_backup.tar.gz personality/memory/

# Restore from backup
tar -xzf anna_memory_backup.tar.gz
```

---

## Troubleshooting

### Connection Issues

```bash
# Check Ollama connection
curl http://localhost:11434/api/tags

# Check API server
curl http://localhost:8000/health
```

### High Memory Usage

```bash
# Check memory consumption
ps aux | grep python

# Reduce max context
# Edit .env: MAX_CONTEXT=10

# Enable memory optimization
# Edit .env: GPU_MEMORY_OPTIMIZE=true
```

### Slow Response Times

```bash
# Check API metrics
curl http://localhost:5000/metrics

# Reduce search results
# Edit .env: MEMORY_SEARCH_RESULTS=1

# Enable caching with Redis
docker compose --profile optional up -d
```

### Log Issues

```bash
# Check log directory
du -sh logs/

# Rotate logs
mv logs/app.json logs/app.json.bak
mv logs/api.json logs/api.json.bak

# Clear old logs (older than 30 days)
find logs/ -name "*.json" -mtime +30 -delete
```

---

## Support

For deployment issues:

1. Check health status: `python main.py --check`
2. Review logs: `tail -f logs/error*.log`
3. Run tests: `pytest -v`
4. Check GitHub issues: https://github.com/KryptykBioz/Anna_AI/issues

---

**Last Updated**: 2024-01-17  
**Version**: 2.0 (Phase 2)
