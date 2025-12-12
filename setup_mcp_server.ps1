# PowerShell script to set up MCP server configuration for FHE Sentiment Analysis

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  MCP Server Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$mcpConfigDir = "$env:USERPROFILE\.mcp"
$serverConfigDir = "$mcpConfigDir\servers"
$projectConfigFile = "$serverConfigDir\fhe-sentiment-analysis.json"

# Create MCP config directory if it doesn't exist
if (-not (Test-Path $mcpConfigDir)) {
    New-Item -ItemType Directory -Path $mcpConfigDir -Force | Out-Null
    Write-Host "✓ Created MCP config directory" -ForegroundColor Green
}

if (-not (Test-Path $serverConfigDir)) {
    New-Item -ItemType Directory -Path $serverConfigDir -Force | Out-Null
    Write-Host "✓ Created MCP servers directory" -ForegroundColor Green
}

# Get the current project directory
$projectDir = (Get-Location).Path

# Create MCP server configuration
$mcpConfig = @{
    name = "fhe-sentiment-analysis"
    description = "FHE Sentiment Analysis Server - Runs sentiment analysis with Fully Homomorphic Encryption"
    command = "docker"
    args = @(
        "run",
        "--rm",
        "-it",
        "-v", "${projectDir}:/app",
        "-v", "${projectDir}/models:/app/models",
        "-p", "7860:7860",
        "-p", "8000:8000",
        "-p", "3000:3000",
        "zamafhe/concrete-ml:latest",
        "python", "run_all.py"
    )
    env = @{
        PYTHONUNBUFFERED = "1"
        MCP_MODE = "docker"
    }
} | ConvertTo-Json -Depth 10

# Write configuration file
$mcpConfig | Out-File -FilePath $projectConfigFile -Encoding UTF8
Write-Host "✓ Created MCP server configuration" -ForegroundColor Green
Write-Host "  Location: $projectConfigFile" -ForegroundColor Gray

Write-Host ""
Write-Host "MCP Server Configuration:" -ForegroundColor Cyan
Write-Host "  Name: fhe-sentiment-analysis" -ForegroundColor White
Write-Host "  Project Directory: $projectDir" -ForegroundColor White
Write-Host "  Docker Image: zamafhe/concrete-ml:latest" -ForegroundColor White
Write-Host "  Ports: 7860 (Gradio), 8000 (API), 3000 (Next.js)" -ForegroundColor White

Write-Host ""
Write-Host "✓ MCP server configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Cyan
Write-Host "1. Use MCP Tool Kit to manage this server" -ForegroundColor White
Write-Host "2. Run: .\run_mcp.ps1 to start via MCP" -ForegroundColor White
Write-Host "3. Or use the MCP Tool Kit launcher directly" -ForegroundColor White

