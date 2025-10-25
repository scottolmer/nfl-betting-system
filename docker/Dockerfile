FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY prompts/ ./prompts/
COPY results/ ./results/

# Create necessary directories
RUN mkdir -p \
    /app/data/lines \
    /app/data/results_tracking \
    /app/data/weekly_data \
    /app/results/line_alerts \
    /app/results/calibration \
    /app/results/backtesting \
    /app/logs

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

# Default command
CMD ["python", "scripts/slack_bot/app.py"]
