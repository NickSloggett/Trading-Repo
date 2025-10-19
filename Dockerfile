# Multi-stage build for optimized image size
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=100

# Set work directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt python-algorithms/requirements.txt ./
RUN cat python-algorithms/requirements.txt >> requirements.txt || true

# Install Python dependencies with improved caching
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with home directory
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    mkdir -p /app && chown -R app:app /app

# Copy installed packages from builder
COPY --from=builder --chown=app:app /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder --chown=app:app /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy project files with proper ownership
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/api/status || exit 1

# Expose port for Jupyter
EXPOSE 8888

# Default command: Jupyter with optimized settings
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]

# For running scripts: docker run --rm -v $(pwd):/app trading-repo python python-algorithms/backtesting/example_ma_crossover.py

