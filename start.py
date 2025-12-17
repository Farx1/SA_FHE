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
        print("[ERREUR] Modele non trouve!")
        print("\n[INFO] Vous devez d'abord entrainer le modele:")
        print("   python train_model_simple.py\n")
        return False
    print("[OK] Modele trouve")
    return True

def check_npm():
    """Vérifie si npm est installé."""
    try:
        # Utiliser shell=True sur Windows pour trouver npm dans le PATH
        use_shell = sys.platform == "win32"
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            check=True,
            shell=use_shell
        )
        version = result.stdout.decode().strip()
        print(f"[OK] npm detecte (version {version})")
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERREUR] npm n'est pas installe")
        print("\n[INFO] Installez Node.js depuis https://nodejs.org/")
        return False, None

def check_webapp_dependencies():
    """Vérifie et installe les dépendances Next.js si nécessaire."""
    web_app_path = Path("web-app")
    node_modules = web_app_path / "node_modules"
    
    if not node_modules.exists():
        print("[INFO] Installation des dependances Next.js...")
        try:
            use_shell = sys.platform == "win32"
            subprocess.run(
                ["npm", "install"],
                cwd=str(web_app_path),
                check=True,
                shell=use_shell
            )
            print("[OK] Dependances installees")
        except subprocess.CalledProcessError:
            print("[ERREUR] Erreur lors de l'installation des dependances")
            return False
    else:
        print("[OK] Dependances Next.js deja installees")
    
    return True

def start_api():
    """Démarre le serveur API Flask."""
    print("\n[API] Demarrage du serveur API Flask (port 8002)...")
    
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
        print(f"[ERREUR] Erreur lors du demarrage de l'API:")
        print(stderr)
        return None
    
    print("[OK] API demarree sur http://localhost:8002")
    return api_process

def start_nextjs():
    """Démarre l'application Next.js."""
    print("\n[NEXTJS] Demarrage de l'application Next.js...")
    
    web_app_path = Path("web-app")
    use_shell = sys.platform == "win32"
    nextjs_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(web_app_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=use_shell
    )
    
    # Attendre un peu pour que Next.js démarre
    time.sleep(5)
    
    if nextjs_process.poll() is not None:
        # Le processus s'est terminé (erreur)
        stdout, stderr = nextjs_process.communicate()
        print(f"[ERREUR] Erreur lors du demarrage de Next.js:")
        print(stderr)
        return None
    
    print("[OK] Next.js demarre sur http://localhost:3000")
    return nextjs_process

def cleanup_processes(api_process, nextjs_process):
    """Arrête proprement les processus."""
    print("\n\n[ARRET] Arret des serveurs...")
    
    if api_process and api_process.poll() is None:
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
            print("[OK] API arretee")
        except subprocess.TimeoutExpired:
            api_process.kill()
            print("[OK] API arretee (force)")
    
    if nextjs_process and nextjs_process.poll() is None:
        nextjs_process.terminate()
        try:
            nextjs_process.wait(timeout=5)
            print("[OK] Next.js arrete")
        except subprocess.TimeoutExpired:
            nextjs_process.kill()
            print("[OK] Next.js arrete (force)")

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
    print("  [SUCCES] Application demarree avec succes!")
    print("="*70)
    print("\n[URLS] URLs disponibles:")
    print("   - Frontend: http://localhost:3000")
    print("   - API:      http://localhost:8002")
    print("\n[INFO] Appuyez sur Ctrl+C pour arreter les serveurs\n")
    
    # 7. Attendre l'interruption
    try:
        # Afficher les logs en temps réel
        while True:
            # Vérifier que les processus tournent toujours
            if api_process.poll() is not None:
                print("\n[WARNING] L'API s'est arretee")
                break
            if nextjs_process.poll() is not None:
                print("\n[WARNING] Next.js s'est arrete")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes(api_process, nextjs_process)
        print("\n[OK] Application arretee\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Interruption par l'utilisateur")
        sys.exit(0)

