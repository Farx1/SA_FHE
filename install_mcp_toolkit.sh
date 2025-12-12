#!/bin/bash
# Bash script to install MCP Tool Kit for Docker
# This script installs MCP Tool Kit and configures it for the FHE Sentiment Analysis project

echo "=========================================="
echo "  MCP Tool Kit Installation"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker detected: $(docker --version)"
echo ""
echo "📥 Installing MCP Tool Kit..."
echo ""

# Install MCP Tool Kit using the official installer
if bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh); then
    echo ""
    echo "✓ MCP Tool Kit installed successfully"
else
    echo "❌ Failed to install MCP Tool Kit automatically"
    echo ""
    echo "Manual installation:"
    echo "1. Open Terminal"
    echo "2. Run: bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)"
    exit 1
fi

echo ""
echo "✓ MCP Tool Kit installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./setup_mcp_server.sh to configure MCP server for this project"
echo "2. Run: ./run_mcp.sh to start the project via MCP"

