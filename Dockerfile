# Multi-stage build for optimized image size and security
FROM python:3.13-slim as builder

# Set environment variables for security and performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry for better dependency management
RUN pip install poetry==1.8.3

# Set work directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual environment in container
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --only=main --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.13-slim

# Metadata labels
LABEL maintainer="Nick Sloggett <nick.sloggett@gmail.com>" \
      description="Trading Development Platform" \
      version="0.1.0"

# Set environment variables for security and performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH" \
    # Security settings
    USER=app \
    UID=1000 \
    GID=1000

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid $GID $USER && \
    useradd --create-home --shell /bin/bash --uid $UID --gid $GID $USER && \
    mkdir -p /app && \
    chown -R $USER:$USER /app

# Copy installed packages from builder
COPY --from=builder --chown=$USER:$USER /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder --chown=$USER:$USER /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy project files with proper ownership
COPY --chown=$USER:$USER . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/notebooks && \
    chown -R $USER:$USER /app/data /app/logs /app/notebooks

# Switch to non-root user
USER $USER

# Health check for web services
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose ports
EXPOSE 8888 8000

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command: Jupyter Lab with security settings
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--ServerApp.token=''","--ServerApp.password=''","--ServerApp.allow_origin='*'"]

# Alternative commands for different use cases:
# For running scripts: docker run --rm -v $(pwd):/app trading-repo python python_algorithms/backtesting/example_ma_crossover.py
# For CLI usage: docker run --rm -v $(pwd):/app trading-repo python -m trading_repo.cli

