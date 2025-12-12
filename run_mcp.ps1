# PowerShell script to run the FHE Sentiment Analysis project via MCP Tool Kit

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  FHE Sentiment Analysis - MCP Mode" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if MCP Tool Kit is installed
$mcpToolKitPath = "$env:USERPROFILE\mcp-tool-kit"
if (-not (Test-Path $mcpToolKitPath)) {
    Write-Host "⚠️  MCP Tool Kit not found" -ForegroundColor Yellow
    Write-Host "Installing MCP Tool Kit..." -ForegroundColor Cyan
    & .\install_mcp_toolkit.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install MCP Tool Kit" -ForegroundColor Red
        exit 1
    }
}

# Check if MCP server is configured
$mcpConfigFile = "$env:USERPROFILE\.mcp\servers\fhe-sentiment-analysis.json"
if (-not (Test-Path $mcpConfigFile)) {
    Write-Host "⚠️  MCP server not configured" -ForegroundColor Yellow
    Write-Host "Setting up MCP server configuration..." -ForegroundColor Cyan
    & .\setup_mcp_server.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to configure MCP server" -ForegroundColor Red
        exit 1
    }
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting FHE Sentiment Analysis via MCP..." -ForegroundColor Cyan
Write-Host ""

# Parse command
$command = if ($args.Count -gt 0) { $args[0] } else { "all" }
$currentDir = (Get-Location).Path

switch ($command) {
    "train" {
        Write-Host "🚀 Training model in Docker with REAL FHE..." -ForegroundColor Cyan
        docker pull zamafhe/concrete-ml:latest
        docker run --rm -it `
            -v "${currentDir}:/app" `
            -v "${currentDir}/models:/app/models" `
            zamafhe/concrete-ml:latest `
            python train_model_simple.py
    }
    "test" {
        Write-Host "🧪 Testing model in Docker..." -ForegroundColor Cyan
        docker run --rm -it `
            -v "${currentDir}:/app" `
            -v "${currentDir}/models:/app/models" `
            zamafhe/concrete-ml:latest `
            python test_model_quality.py
    }
    "gradio" {
        Write-Host "🎨 Launching Gradio interface with REAL FHE..." -ForegroundColor Cyan
        Write-Host "   Available at http://localhost:7860" -ForegroundColor Green
        docker pull zamafhe/concrete-ml:latest
        docker run --rm -it `
            -v "${currentDir}:/app" `
            -v "${currentDir}/models:/app/models" `
            -p 7860:7860 `
            zamafhe/concrete-ml:latest `
            python client.py
    }
    "api" {
        Write-Host "📡 Launching Flask API..." -ForegroundColor Cyan
        Write-Host "   Available at http://localhost:8000" -ForegroundColor Green
        docker run --rm -it `
            -v "${currentDir}:/app" `
            -v "${currentDir}/models:/app/models" `
            -p 8000:8000 `
            zamafhe/concrete-ml:latest `
            python api_server.py
    }
    "mcp-server" {
        Write-Host "🔌 Starting MCP server mode..." -ForegroundColor Cyan
        Write-Host "   This will start the MCP server for integration with Claude Desktop" -ForegroundColor Yellow
        Write-Host ""
        
        # Check if MCP Tool Kit launcher exists
        $launcherPath = "$mcpToolKitPath\launch.ps1"
        if (Test-Path $launcherPath) {
            Write-Host "Launching MCP Tool Kit..." -ForegroundColor Cyan
            & $launcherPath
        } else {
            Write-Host "⚠️  MCP Tool Kit launcher not found" -ForegroundColor Yellow
            Write-Host "Using direct Docker command instead..." -ForegroundColor Cyan
            docker run --rm -it `
                -v "${currentDir}:/app" `
                -v "${currentDir}/models:/app/models" `
                -p 7860:7860 `
                -p 8000:8000 `
                -p 3000:3000 `
                zamafhe/concrete-ml:latest `
                python run_all.py
        }
    }
    "all" {
        Write-Host "🚀 Running complete workflow via MCP..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "This will:" -ForegroundColor Yellow
        Write-Host "  1. Pull the Concrete-ML Docker image (first time only)" -ForegroundColor White
        Write-Host "  2. Train the model with REAL FHE" -ForegroundColor White
        Write-Host "  3. Test the model" -ForegroundColor White
        Write-Host "  4. Launch the application" -ForegroundColor White
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  .\run_mcp.ps1 train       - Train the model" -ForegroundColor White
        Write-Host "  .\run_mcp.ps1 test        - Test the model" -ForegroundColor White
        Write-Host "  .\run_mcp.ps1 gradio      - Launch Gradio interface" -ForegroundColor White
        Write-Host "  .\run_mcp.ps1 api         - Launch Flask API" -ForegroundColor White
        Write-Host "  .\run_mcp.ps1 mcp-server   - Start MCP server mode" -ForegroundColor White
        Write-Host ""
        Write-Host "Starting complete workflow..." -ForegroundColor Cyan
        Write-Host "Note: First run will download the Docker image (~2GB)" -ForegroundColor Yellow
        Write-Host ""
        
        # Pull the image first
        Write-Host "📥 Pulling Concrete-ML Docker image..." -ForegroundColor Cyan
        docker pull zamafhe/concrete-ml:latest
        
        Write-Host "🚀 Starting workflow..." -ForegroundColor Green
        docker run --rm -it `
            -v "${currentDir}:/app" `
            -v "${currentDir}/models:/app/models" `
            -p 7860:7860 `
            -p 8000:8000 `
            -p 3000:3000 `
            zamafhe/concrete-ml:latest `
            python run_all.py
    }
    default {
        Write-Host "Unknown command: $command" -ForegroundColor Red
        Write-Host "Use: train, test, gradio, api, mcp-server, or all" -ForegroundColor Yellow
        exit 1
    }
}

