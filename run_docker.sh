#!/bin/bash
# Script to run the FHE Sentiment Analysis project in Docker

set -e

echo "=========================================="
echo "  FHE Sentiment Analysis - Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ docker-compose is not available"
    echo "Please install docker-compose or use Docker Desktop"
    exit 1
fi

echo "✓ Docker detected"
echo ""

# Build the image
echo "🔨 Building Docker image..."
$COMPOSE_CMD build

echo ""
echo "=========================================="
echo "  Container ready!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  ./run_docker.sh train    - Train the model"
echo "  ./run_docker.sh test     - Test the model"
echo "  ./run_docker.sh gradio   - Launch Gradio interface"
echo "  ./run_docker.sh api      - Launch Flask API"
echo "  ./run_docker.sh shell    - Open shell in container"
echo "  ./run_docker.sh all      - Run everything (train → test → launch)"
echo ""

# Parse command
COMMAND=${1:-all}

case $COMMAND in
    train)
        echo "🚀 Training model in Docker..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            -p 7860:7860 \
            -p 8000:8000 \
            zamafhe/concrete-ml:latest \
            python train_model_simple.py
        ;;
    test)
        echo "🧪 Testing model in Docker..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            zamafhe/concrete-ml:latest \
            python test_model_quality.py
        ;;
    gradio)
        echo "🎨 Launching Gradio interface..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            -p 7860:7860 \
            zamafhe/concrete-ml:latest \
            python client.py
        ;;
    api)
        echo "📡 Launching Flask API..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            -p 8000:8000 \
            zamafhe/concrete-ml:latest \
            python api_server.py
        ;;
    shell)
        echo "🐚 Opening shell in container..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            zamafhe/concrete-ml:latest \
            /bin/bash
        ;;
    all)
        echo "🚀 Running complete workflow..."
        docker run --rm -it \
            -v "$(pwd):/app" \
            -v "$(pwd)/models:/app/models" \
            -p 7860:7860 \
            -p 8000:8000 \
            zamafhe/concrete-ml:latest \
            python run_all.py
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Use: train, test, gradio, api, shell, or all"
        exit 1
        ;;
esac

