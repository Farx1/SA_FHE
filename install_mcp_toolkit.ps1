# PowerShell script to install MCP Tool Kit for Docker
# This script installs MCP Tool Kit and configures it for the FHE Sentiment Analysis project

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  MCP Tool Kit Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker detected: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📥 Installing MCP Tool Kit..." -ForegroundColor Cyan
Write-Host ""

# Install MCP Tool Kit using the official installer
try {
    $installScript = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1" -UseBasicParsing
    Invoke-Expression $installScript.Content
    Write-Host "✓ MCP Tool Kit installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install MCP Tool Kit automatically" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "1. Open PowerShell as Administrator" -ForegroundColor White
    Write-Host "2. Run: irm https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1 | iex" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "✓ MCP Tool Kit installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\setup_mcp_server.ps1 to configure MCP server for this project" -ForegroundColor White
Write-Host "2. Run: .\run_mcp.ps1 to start the project via MCP" -ForegroundColor White

