FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ffmpeg for subtitle generation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads logs credentials

# Expose ports
EXPOSE 8000 8501

# Default command - use PORT env var if available, otherwise 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
