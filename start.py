"""
Script simple pour lancer l'application complète (API Flask + Next.js)
Usage: python start.py
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def print_header():
    """Affiche l'en-tête du script."""
    print("\n" + "="*70)
    print("  FHE Sentiment Analysis - Démarrage")
    print("="*70 + "\n")

def check_model():
    """Vérifie que le modèle est entraîné."""
    model_path = Path("models/sentiment_fhe_model/model_with_simulator.pkl")
    if not model_path.exists():
        print("❌ Modèle non trouvé!")
        print("\n💡 Vous devez d'abord entraîner le modèle:")
        print("   python train_model_simple.py\n")
        return False
    print("✓ Modèle trouvé")
    return True

def check_npm():
    """Vérifie si npm est installé."""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            check=True
        )
        version = result.stdout.decode().strip()
        print(f"✓ npm détecté (version {version})")
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm n'est pas installé")
        print("\n💡 Installez Node.js depuis https://nodejs.org/")
        return False, None

def check_webapp_dependencies():
    """Vérifie et installe les dépendances Next.js si nécessaire."""
    web_app_path = Path("web-app")
    node_modules = web_app_path / "node_modules"
    
    if not node_modules.exists():
        print("⚠️  Installation des dépendances Next.js...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(web_app_path),
                check=True
            )
            print("✓ Dépendances installées")
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances")
            return False
    else:
        print("✓ Dépendances Next.js déjà installées")
    
    return True

def start_api():
    """Démarre le serveur API Flask."""
    print("\n📡 Démarrage du serveur API Flask (port 8002)...")
    
    api_process = subprocess.Popen(
        [sys.executable, "api_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Attendre un peu pour vérifier que l'API démarre
    time.sleep(3)
    
    if api_process.poll() is not None:
        # Le processus s'est terminé (erreur)
        stdout, stderr = api_process.communicate()
        print(f"❌ Erreur lors du démarrage de l'API:")
        print(stderr)
        return None
    
    print("✓ API démarrée sur http://localhost:8002")
    return api_process

def start_nextjs():
    """Démarre l'application Next.js."""
    print("\n🌐 Démarrage de l'application Next.js...")
    
    web_app_path = Path("web-app")
    nextjs_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(web_app_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Attendre un peu pour que Next.js démarre
    time.sleep(5)
    
    if nextjs_process.poll() is not None:
        # Le processus s'est terminé (erreur)
        stdout, stderr = nextjs_process.communicate()
        print(f"❌ Erreur lors du démarrage de Next.js:")
        print(stderr)
        return None
    
    print("✓ Next.js démarré sur http://localhost:3000")
    return nextjs_process

def cleanup_processes(api_process, nextjs_process):
    """Arrête proprement les processus."""
    print("\n\n🛑 Arrêt des serveurs...")
    
    if api_process and api_process.poll() is None:
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
            print("✓ API arrêtée")
        except subprocess.TimeoutExpired:
            api_process.kill()
            print("✓ API arrêtée (forcé)")
    
    if nextjs_process and nextjs_process.poll() is None:
        nextjs_process.terminate()
        try:
            nextjs_process.wait(timeout=5)
            print("✓ Next.js arrêté")
        except subprocess.TimeoutExpired:
            nextjs_process.kill()
            print("✓ Next.js arrêté (forcé)")

def main():
    """Fonction principale."""
    print_header()
    
    # 1. Vérifier le modèle
    if not check_model():
        sys.exit(1)
    
    # 2. Vérifier npm
    npm_available, npm_version = check_npm()
    if not npm_available:
        sys.exit(1)
    
    # 3. Vérifier/installer les dépendances Next.js
    if not check_webapp_dependencies():
        sys.exit(1)
    
    # 4. Démarrer l'API
    api_process = start_api()
    if api_process is None:
        sys.exit(1)
    
    # 5. Démarrer Next.js
    nextjs_process = start_nextjs()
    if nextjs_process is None:
        cleanup_processes(api_process, None)
        sys.exit(1)
    
    # 6. Afficher les informations
    print("\n" + "="*70)
    print("  ✅ Application démarrée avec succès!")
    print("="*70)
    print("\n📍 URLs disponibles:")
    print("   - Frontend: http://localhost:3000")
    print("   - API:      http://localhost:8002")
    print("\n💡 Appuyez sur Ctrl+C pour arrêter les serveurs\n")
    
    # 7. Attendre l'interruption
    try:
        # Afficher les logs en temps réel
        while True:
            # Vérifier que les processus tournent toujours
            if api_process.poll() is not None:
                print("\n⚠️  L'API s'est arrêtée")
                break
            if nextjs_process.poll() is not None:
                print("\n⚠️  Next.js s'est arrêté")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes(api_process, nextjs_process)
        print("\n✓ Application arrêtée\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        sys.exit(0)

