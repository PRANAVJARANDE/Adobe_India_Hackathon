# Challenge 1A: PDF Heading Extraction
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create input and output directories
RUN mkdir -p input output

# Set environment variables
ENV INPUT_DIR=input
ENV OUTPUT_DIR=output

# Run the application
CMD ["python", "main.py"]