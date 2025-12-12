#!/bin/bash
# Bash script to set up MCP server configuration for FHE Sentiment Analysis

echo "=========================================="
echo "  MCP Server Configuration"
echo "=========================================="
echo ""

MCP_CONFIG_DIR="$HOME/.mcp"
SERVER_CONFIG_DIR="$MCP_CONFIG_DIR/servers"
PROJECT_CONFIG_FILE="$SERVER_CONFIG_DIR/fhe-sentiment-analysis.json"

# Create MCP config directory if it doesn't exist
mkdir -p "$MCP_CONFIG_DIR"
mkdir -p "$SERVER_CONFIG_DIR"

if [ ! -d "$MCP_CONFIG_DIR" ]; then
    echo "✓ Created MCP config directory"
fi

if [ ! -d "$SERVER_CONFIG_DIR" ]; then
    echo "✓ Created MCP servers directory"
fi

# Get the current project directory
PROJECT_DIR=$(pwd)

# Create MCP server configuration JSON
cat > "$PROJECT_CONFIG_FILE" << EOF
{
  "name": "fhe-sentiment-analysis",
  "description": "FHE Sentiment Analysis Server - Runs sentiment analysis with Fully Homomorphic Encryption",
  "command": "docker",
  "args": [
    "run",
    "--rm",
    "-it",
    "-v", "${PROJECT_DIR}:/app",
    "-v", "${PROJECT_DIR}/models:/app/models",
    "-p", "7860:7860",
    "-p", "8000:8000",
    "-p", "3000:3000",
    "zamafhe/concrete-ml:latest",
    "python", "run_all.py"
  ],
  "env": {
    "PYTHONUNBUFFERED": "1",
    "MCP_MODE": "docker"
  }
}
EOF

echo "✓ Created MCP server configuration"
echo "  Location: $PROJECT_CONFIG_FILE"

echo ""
echo "MCP Server Configuration:"
echo "  Name: fhe-sentiment-analysis"
echo "  Project Directory: $PROJECT_DIR"
echo "  Docker Image: zamafhe/concrete-ml:latest"
echo "  Ports: 7860 (Gradio), 8000 (API), 3000 (Next.js)"

echo ""
echo "✓ MCP server configuration complete!"
echo ""
echo "You can now:"
echo "1. Use MCP Tool Kit to manage this server"
echo "2. Run: ./run_mcp.sh to start via MCP"
echo "3. Or use the MCP Tool Kit launcher directly"

