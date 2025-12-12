#!/bin/bash
# Bash script to run the FHE Sentiment Analysis project via MCP Tool Kit

echo "=========================================="
echo "  FHE Sentiment Analysis - MCP Mode"
echo "=========================================="
echo ""

# Check if MCP Tool Kit is installed
MCP_TOOLKIT_PATH="$HOME/mcp-tool-kit"
if [ ! -d "$MCP_TOOLKIT_PATH" ]; then
    echo "⚠️  MCP Tool Kit not found"
    echo "Installing MCP Tool Kit..."
    bash ./install_mcp_toolkit.sh
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install MCP Tool Kit"
        exit 1
    fi
fi

# Check if MCP server is configured
MCP_CONFIG_FILE="$HOME/.mcp/servers/fhe-sentiment-analysis.json"
if [ ! -f "$MCP_CONFIG_FILE" ]; then
    echo "⚠️  MCP server not configured"
    echo "Setting up MCP server configuration..."
    bash ./setup_mcp_server.sh
    if [ $? -ne 0 ]; then
        echo "❌ Failed to configure MCP server"
        exit 1
    fi
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""
echo "🚀 Starting FHE Sentiment Analysis via MCP..."
echo ""

# Parse command
COMMAND=${1:-all}
CURRENT_DIR=$(pwd)

case $COMMAND in
    train)
        echo "🚀 Training model in Docker with REAL FHE..."
        docker pull zamafhe/concrete-ml:latest
        docker run --rm -it \
            -v "${CURRENT_DIR}:/app" \
            -v "${CURRENT_DIR}/models:/app/models" \
            zamafhe/concrete-ml:latest \
            python train_model_simple.py
        ;;
    test)
        echo "🧪 Testing model in Docker..."
        docker run --rm -it \
            -v "${CURRENT_DIR}:/app" \
            -v "${CURRENT_DIR}/models:/app/models" \
            zamafhe/concrete-ml:latest \
            python test_model_quality.py
        ;;
    gradio)
        echo "🎨 Launching Gradio interface with REAL FHE..."
        echo "   Available at http://localhost:7860"
        docker pull zamafhe/concrete-ml:latest
        docker run --rm -it \
            -v "${CURRENT_DIR}:/app" \
            -v "${CURRENT_DIR}/models:/app/models" \
            -p 7860:7860 \
            zamafhe/concrete-ml:latest \
            python client.py
        ;;
    api)
        echo "📡 Launching Flask API..."
        echo "   Available at http://localhost:8000"
        docker run --rm -it \
            -v "${CURRENT_DIR}:/app" \
            -v "${CURRENT_DIR}/models:/app/models" \
            -p 8000:8000 \
            zamafhe/concrete-ml:latest \
            python api_server.py
        ;;
    mcp-server)
        echo "🔌 Starting MCP server mode..."
        echo "   This will start the MCP server for integration with Claude Desktop"
        echo ""
        
        # Check if MCP Tool Kit launcher exists
        LAUNCHER_PATH="$MCP_TOOLKIT_PATH/launch.sh"
        if [ -f "$LAUNCHER_PATH" ]; then
            echo "Launching MCP Tool Kit..."
            bash "$LAUNCHER_PATH"
        else
            echo "⚠️  MCP Tool Kit launcher not found"
            echo "Using direct Docker command instead..."
            docker run --rm -it \
                -v "${CURRENT_DIR}:/app" \
                -v "${CURRENT_DIR}/models:/app/models" \
                -p 7860:7860 \
                -p 8000:8000 \
                -p 3000:3000 \
                zamafhe/concrete-ml:latest \
                python run_all.py
        fi
        ;;
    all)
        echo "🚀 Running complete workflow via MCP..."
        echo ""
        echo "This will:"
        echo "  1. Pull the Concrete-ML Docker image (first time only)"
        echo "  2. Train the model with REAL FHE"
        echo "  3. Test the model"
        echo "  4. Launch the application"
        echo ""
        echo "Available commands:"
        echo "  ./run_mcp.sh train       - Train the model"
        echo "  ./run_mcp.sh test        - Test the model"
        echo "  ./run_mcp.sh gradio      - Launch Gradio interface"
        echo "  ./run_mcp.sh api         - Launch Flask API"
        echo "  ./run_mcp.sh mcp-server   - Start MCP server mode"
        echo ""
        echo "Starting complete workflow..."
        echo "Note: First run will download the Docker image (~2GB)"
        echo ""
        
        # Pull the image first
        echo "📥 Pulling Concrete-ML Docker image..."
        docker pull zamafhe/concrete-ml:latest
        
        echo "🚀 Starting workflow..."
        docker run --rm -it \
            -v "${CURRENT_DIR}:/app" \
            -v "${CURRENT_DIR}/models:/app/models" \
            -p 7860:7860 \
            -p 8000:8000 \
            -p 3000:3000 \
            zamafhe/concrete-ml:latest \
            python run_all.py
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Use: train, test, gradio, api, mcp-server, or all"
        exit 1
        ;;
esac

