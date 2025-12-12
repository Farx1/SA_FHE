# PowerShell script to run the FHE Sentiment Analysis project in Docker

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  FHE Sentiment Analysis - Docker Setup" -ForegroundColor Cyan
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

# Check if docker-compose is available
$composeCmd = $null
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $composeCmd = "docker-compose"
} else {
    try {
        $null = docker compose version 2>&1
        $composeCmd = "docker compose"
    } catch {
        Write-Host "⚠️  docker-compose not found, using direct docker commands" -ForegroundColor Yellow
    }
}

Write-Host ""

# Parse command
$command = if ($args.Count -gt 0) { $args[0] } else { "all" }

$currentDir = (Get-Location).Path

switch ($command) {
    "train" {
        Write-Host "🚀 Training model in Docker with REAL FHE..." -ForegroundColor Cyan
        Write-Host "📥 Pulling Docker image if needed..." -ForegroundColor Yellow
        docker pull zamafhe/concrete-ml:latest
        Write-Host ""
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" -p 7860:7860 -p 8000:8000 zamafhe/concrete-ml:latest python train_model_simple.py
    }
    "test" {
        Write-Host "🧪 Testing model in Docker..." -ForegroundColor Cyan
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" zamafhe/concrete-ml:latest python test_model_quality.py
    }
    "gradio" {
        Write-Host "🎨 Launching Gradio interface with REAL FHE..." -ForegroundColor Cyan
        Write-Host "   Available at http://localhost:7860" -ForegroundColor Green
        Write-Host "📥 Pulling Docker image if needed..." -ForegroundColor Yellow
        docker pull zamafhe/concrete-ml:latest
        Write-Host ""
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" -p 7860:7860 zamafhe/concrete-ml:latest python client.py
    }
    "api" {
        Write-Host "📡 Launching Flask API..." -ForegroundColor Cyan
        Write-Host "   Available at http://localhost:8000" -ForegroundColor Green
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" -p 8000:8000 zamafhe/concrete-ml:latest python api_server.py
    }
    "shell" {
        Write-Host "🐚 Opening shell in container..." -ForegroundColor Cyan
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" zamafhe/concrete-ml:latest /bin/bash
    }
    "all" {
        Write-Host "🚀 Running complete workflow..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "This will:" -ForegroundColor Yellow
        Write-Host "  1. Pull the Concrete-ML Docker image (first time only)" -ForegroundColor White
        Write-Host "  2. Train the model with REAL FHE" -ForegroundColor White
        Write-Host "  3. Test the model" -ForegroundColor White
        Write-Host "  4. Launch the application" -ForegroundColor White
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  .\run_docker.ps1 train    - Train the model" -ForegroundColor White
        Write-Host "  .\run_docker.ps1 test     - Test the model" -ForegroundColor White
        Write-Host "  .\run_docker.ps1 gradio   - Launch Gradio interface" -ForegroundColor White
        Write-Host "  .\run_docker.ps1 api      - Launch Flask API" -ForegroundColor White
        Write-Host "  .\run_docker.ps1 shell    - Open shell in container" -ForegroundColor White
        Write-Host ""
        Write-Host "Starting complete workflow..." -ForegroundColor Cyan
        Write-Host "Note: First run will download the Docker image (~2GB)" -ForegroundColor Yellow
        Write-Host ""
        
        # Pull the image first
        Write-Host "📥 Pulling Concrete-ML Docker image..." -ForegroundColor Cyan
        docker pull zamafhe/concrete-ml:latest
        
        Write-Host "🚀 Starting workflow..." -ForegroundColor Green
        docker run --rm -it -v "${currentDir}:/app" -v "${currentDir}/models:/app/models" -p 7860:7860 -p 8000:8000 zamafhe/concrete-ml:latest python run_all.py
    }
    default {
        Write-Host "Unknown command: $command" -ForegroundColor Red
        Write-Host "Use: train, test, gradio, api, shell, or all" -ForegroundColor Yellow
        exit 1
    }
}

