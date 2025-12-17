# PowerShell script pour lancer l'application complète (API Flask + Next.js)
# Usage: .\start.ps1

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "  FHE Sentiment Analysis - Démarrage" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le modèle existe
$modelPath = "models\sentiment_fhe_model\model_with_simulator.pkl"
if (-not (Test-Path $modelPath)) {
    Write-Host "❌ Modèle non trouvé!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vous devez d'abord entraîner le modèle:" -ForegroundColor Yellow
    Write-Host "   python train_model_simple.py" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host "✓ Modèle trouvé" -ForegroundColor Green

# Vérifier npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm détecté (version $npmVersion)" -ForegroundColor Green
} catch {
    Write-Host "❌ npm n'est pas installé" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Installez Node.js depuis https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Vérifier/installer les dépendances Next.js
$webAppPath = "web-app"
$nodeModules = Join-Path $webAppPath "node_modules"

if (-not (Test-Path $nodeModules)) {
    Write-Host "⚠️  Installation des dépendances Next.js..." -ForegroundColor Yellow
    Set-Location $webAppPath
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    Set-Location ..
    Write-Host "✓ Dépendances installées" -ForegroundColor Green
} else {
    Write-Host "✓ Dépendances Next.js déjà installées" -ForegroundColor Green
}

# Fonction pour nettoyer les processus
function Stop-AllProcesses {
    Write-Host ""
    Write-Host "🛑 Arrêt des serveurs..." -ForegroundColor Yellow
    
    if ($apiJob) {
        Stop-Job $apiJob -ErrorAction SilentlyContinue
        Remove-Job $apiJob -ErrorAction SilentlyContinue
        Write-Host "✓ API arrêtée" -ForegroundColor Green
    }
    
    if ($nextjsJob) {
        Stop-Job $nextjsJob -ErrorAction SilentlyContinue
        Remove-Job $nextjsJob -ErrorAction SilentlyContinue
        Write-Host "✓ Next.js arrêté" -ForegroundColor Green
    }
}

# Gérer l'interruption
$null = Register-EngineEvent PowerShell.Exiting -Action {
    Stop-AllProcesses
}

# Démarrer l'API
Write-Host ""
Write-Host "📡 Démarrage du serveur API Flask (port 8002)..." -ForegroundColor Cyan
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python api_server.py
}

Start-Sleep -Seconds 3

# Vérifier que l'API a démarré
$apiJobState = Get-Job $apiJob | Select-Object -ExpandProperty State
if ($apiJobState -eq "Failed" -or $apiJobState -eq "Completed") {
    $apiOutput = Receive-Job $apiJob
    Write-Host "❌ Erreur lors du démarrage de l'API:" -ForegroundColor Red
    Write-Host $apiOutput -ForegroundColor Red
    exit 1
}

Write-Host "✓ API démarrée sur http://localhost:8002" -ForegroundColor Green

# Démarrer Next.js
Write-Host ""
Write-Host "🌐 Démarrage de l'application Next.js..." -ForegroundColor Cyan
$nextjsJob = Start-Job -ScriptBlock {
    Set-Location (Join-Path $using:PWD "web-app")
    npm run dev
}

Start-Sleep -Seconds 5

# Vérifier que Next.js a démarré
$nextjsJobState = Get-Job $nextjsJob | Select-Object -ExpandProperty State
if ($nextjsJobState -eq "Failed") {
    $nextjsOutput = Receive-Job $nextjsJob
    Write-Host "❌ Erreur lors du démarrage de Next.js:" -ForegroundColor Red
    Write-Host $nextjsOutput -ForegroundColor Red
    Stop-AllProcesses
    exit 1
}

Write-Host "✓ Next.js démarré sur http://localhost:3000" -ForegroundColor Green

# Afficher les informations
Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "  ✅ Application démarrée avec succès!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API:      http://localhost:8002" -ForegroundColor White
Write-Host ""
Write-Host "💡 Appuyez sur Ctrl+C pour arrêter les serveurs" -ForegroundColor Yellow
Write-Host ""

# Attendre l'interruption
try {
    while ($true) {
        $apiState = Get-Job $apiJob | Select-Object -ExpandProperty State
        $nextjsState = Get-Job $nextjsJob | Select-Object -ExpandProperty State
        
        if ($apiState -eq "Failed" -or $apiState -eq "Completed") {
            Write-Host "⚠️  L'API s'est arrêtée" -ForegroundColor Yellow
            break
        }
        if ($nextjsState -eq "Failed" -or $nextjsState -eq "Completed") {
            Write-Host "⚠️  Next.js s'est arrêté" -ForegroundColor Yellow
            break
        }
        
        Start-Sleep -Seconds 1
    }
} catch {
    # Ignorer les erreurs d'interruption
} finally {
    Stop-AllProcesses
    Write-Host ""
    Write-Host "✓ Application arrêtée" -ForegroundColor Green
    Write-Host ""
}

