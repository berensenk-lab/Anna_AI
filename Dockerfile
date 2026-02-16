# Multi-stage build for Anna AI
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /tmp/build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels for faster installation in runtime stage
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    portaudio19-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /tmp/build/wheels /wheels
COPY --from=builder /root/.local /root/.local

# Set PATH
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install wheels
COPY requirements.txt .
RUN pip install --no-index --no-deps --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs \
    && mkdir -p personality/memory \
    && mkdir -p personality/base_memory \
    && mkdir -p models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Default command runs GUI, override for CLI with --no-gui
CMD ["python", "main.py"]
