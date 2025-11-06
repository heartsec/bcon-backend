FROM python:3.11-slim

# Install system dependencies including poppler-utils (no git required)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (without dify-client)
COPY requirements.txt .

# Install base dependencies (skip dify-client for now)
RUN grep -v "git+" requirements.txt > requirements-base.txt && \
    pip install --no-cache-dir -r requirements-base.txt

# Download and install dify-client manually
RUN wget https://github.com/langgenius/dify/archive/refs/tags/1.9.2.zip -O dify.zip && \
    unzip -q dify.zip && \
    cd dify-1.9.2/sdks/python-client && \
    pip install --no-cache-dir . && \
    cd /app && \
    rm -rf dify.zip dify-1.9.2

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p cache

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
