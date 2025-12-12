# Dockerfile for FHE Sentiment Analysis with Concrete-ML
# Uses the official Zama Concrete-ML Docker image
FROM zamafhe/concrete-ml:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (without concrete-ml as it's already in the image)
COPY requirements-docker.txt /app/requirements-docker.txt

# Install Python dependencies
RUN pip install --no-cache-dir -U pip wheel setuptools && \
    pip install --no-cache-dir -r requirements-docker.txt

# Copy project files
COPY . /app/

# Create models directory
RUN mkdir -p /app/models

# Expose ports
# 7860 for Gradio
# 8000 for Flask API
# 3000 for Next.js (if used)
EXPOSE 7860 8000 3000

# Default command (can be overridden)
CMD ["python", "run_all.py"]

