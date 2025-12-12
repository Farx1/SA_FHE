"""
Script unique pour tout lancer : entraînement -> tests -> application
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_section(title):
    """Affiche une section avec un titre."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    print_section("VÉRIFICATION DES DÉPENDANCES")
    
    # Mapping: nom d'affichage -> nom d'import
    required_packages = {
        'torch': 'torch',
        'transformers': 'transformers',
        'xgboost': 'xgboost',
        'gradio': 'gradio',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scikit-learn': 'sklearn',  # Le package s'importe comme 'sklearn'
        'datasets': 'datasets',
        'flask': 'flask',
        'flask-cors': 'flask_cors',
        'plotly': 'plotly',
        'tqdm': 'tqdm'
    }
    
    # Packages optionnels (pour Windows, concrete-ml n'est pas disponible)
    optional_packages = {
        'concrete-ml': 'concrete.ml'
    }
    
    missing = []
    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {display_name}")
        except ImportError:
            missing.append(display_name)
            print(f"✗ {display_name} - MANQUANT")
    
    # Vérifier les packages optionnels
    print("\nPackages optionnels:")
    for display_name, import_name in optional_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {display_name} (optionnel - disponible)")
        except ImportError:
            print(f"⚠ {display_name} (optionnel - non disponible, utilise le simulateur FHE)")
    
    if missing:
        print(f"\n❌ Packages manquants: {', '.join(missing)}")
        print("Installez-les avec: pip install scikit-learn flask flask-cors plotly tqdm")
        print("(concrete-ml n'est pas nécessaire sur Windows, le simulateur sera utilisé)")
        return False
    
    print("\n✓ Toutes les dépendances essentielles sont installées")
    return True

def train_model():
    """Entraîne le modèle."""
    print_section("ENTRAÎNEMENT DU MODÈLE")
    
    model_path = Path("models/sentiment_fhe_model/model_with_simulator.pkl")
    
    # Si le modèle existe déjà, demander si on veut le réentraîner
    if model_path.exists():
        print("⚠️  Un modèle existe déjà.")
        response = input("Voulez-vous le réentraîner? (o/n, défaut: n): ").strip().lower()
        if response != 'o':
            print("✓ Utilisation du modèle existant")
            return True
    
    print("🚀 Démarrage de l'entraînement...")
    print("   (Cela peut prendre plusieurs minutes)\n")
    
    try:
        # Exécuter le script d'entraînement
        result = subprocess.run(
            [sys.executable, "train_model_simple.py"],
            check=True,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✓ Entraînement terminé avec succès!")
            return True
        else:
            print("\n❌ Erreur lors de l'entraînement")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de l'entraînement: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Entraînement interrompu par l'utilisateur")
        return False

def test_model():
    """Teste le modèle avec des phrases prédéfinies."""
    print_section("TESTS DU MODÈLE")
    
    model_path = Path("models/sentiment_fhe_model/model_with_simulator.pkl")
    
    if not model_path.exists():
        print("❌ Modèle non trouvé. Veuillez d'abord entraîner le modèle.")
        return False
    
    print("🧪 Exécution des tests de qualité...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_model_quality.py"],
            check=True,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✓ Tests terminés")
            return True
        else:
            print("\n⚠️  Certains tests ont échoué")
            return True  # On continue quand même
            
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️  Erreur lors des tests: {e}")
        # Vérifier si c'est une erreur de mémoire PyTorch
        if "pagination" in str(e).lower() or "1455" in str(e):
            print("\n💡 Problème de mémoire détecté (PyTorch)")
            print("   Solutions possibles:")
            print("   1. Redémarrer votre ordinateur")
            print("   2. Fermer d'autres applications pour libérer de la mémoire")
            print("   3. Augmenter la taille du fichier de pagination Windows")
            print("   4. Les tests sont optionnels, vous pouvez continuer")
        print("   Continuons quand même...")
        return True  # On continue quand même
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus")
        return True

def launch_app():
    """Lance l'application (choix entre Gradio et Next.js)."""
    print_section("LANCEMENT DE L'APPLICATION")
    
    # Vérifier npm pour afficher les options disponibles
    npm_available, npm_version = check_npm()
    
    print("Choisissez l'interface à lancer:")
    print("  1. Gradio (Python) - Interface simple et rapide ✓")
    if npm_available:
        print(f"  2. Next.js (Web moderne) - Interface visuelle complète ✓ (npm {npm_version})")
        print("  3. Les deux (Gradio + Next.js)")
    else:
        print("  2. Next.js (Web moderne) - ❌ npm non disponible")
        print("     Installez Node.js depuis https://nodejs.org/ pour utiliser Next.js")
    
    choice = input("\nVotre choix (1/2/3, défaut: 1): ").strip()
    
    if choice == '2':
        if npm_available:
            launch_nextjs()
        else:
            print("\n❌ npm n'est pas disponible. Utilisation de Gradio à la place...")
            launch_gradio()
    elif choice == '3':
        if npm_available:
            launch_both()
        else:
            print("\n⚠️  npm n'est pas disponible. Lancement de Gradio uniquement...")
            launch_gradio()
    else:
        launch_gradio()

def launch_gradio():
    """Lance l'interface Gradio."""
    print("\n🚀 Lancement de l'interface Gradio...")
    print("   L'interface sera disponible sur http://localhost:7860")
    print("   (Appuyez sur Ctrl+C pour arrêter)\n")
    
    try:
        subprocess.run([sys.executable, "client.py"], check=False)
    except KeyboardInterrupt:
        print("\n\n✓ Interface arrêtée")

def check_npm():
    """Vérifie si npm est installé."""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            check=True
        )
        return True, result.stdout.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None

def launch_nextjs():
    """Lance l'application Next.js avec l'API Python."""
    print("\n🚀 Lancement de l'application Next.js...")
    
    # Vérifier que npm est installé
    npm_available, npm_version = check_npm()
    if not npm_available:
        print("❌ npm n'est pas installé ou n'est pas dans le PATH")
        print("\n💡 Pour installer Node.js et npm:")
        print("   1. Téléchargez Node.js depuis https://nodejs.org/")
        print("   2. Installez-le (npm sera inclus)")
        print("   3. Redémarrez votre terminal")
        print("\n   Ou utilisez l'option 1 (Gradio) qui ne nécessite pas npm")
        return
    
    print(f"✓ npm détecté (version {npm_version})")
    
    # Vérifier que l'API server existe
    if not Path("api_server.py").exists():
        print("❌ api_server.py non trouvé")
        return
    
    # Vérifier que web-app existe
    web_app_path = Path("web-app")
    if not web_app_path.exists():
        print("❌ Dossier web-app non trouvé")
        return
    
    # Vérifier node_modules
    node_modules = web_app_path / "node_modules"
    if not node_modules.exists():
        print("⚠️  node_modules non trouvé. Installation des dépendances...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(web_app_path),
                check=True
            )
            print("✓ Dépendances installées")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation des dépendances: {e}")
            return
        except FileNotFoundError:
            print("❌ npm non trouvé. Veuillez installer Node.js")
            return
    
    print("\n📡 Démarrage du serveur API Python (port 8000)...")
    try:
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'API: {e}")
        return
    
    # Attendre un peu pour que l'API démarre
    time.sleep(3)
    
    print("🌐 Démarrage de l'application Next.js (port 3000)...")
    print("   L'application sera disponible sur http://localhost:3000")
    print("   (Appuyez sur Ctrl+C pour arrêter)\n")
    
    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=str(web_app_path),
            check=False
        )
    except FileNotFoundError:
        print("\n❌ npm non trouvé. Veuillez installer Node.js")
    except KeyboardInterrupt:
        print("\n\n✓ Arrêt de l'application...")
    finally:
        # Arrêter l'API
        if 'api_process' in locals() and api_process.poll() is None:
            print("Arrêt du serveur API...")
            api_process.terminate()
            api_process.wait()

def launch_both():
    """Lance Gradio et Next.js en même temps."""
    print("\n🚀 Lancement des deux interfaces...")
    
    # Vérifier npm pour Next.js
    npm_available, npm_version = check_npm()
    if not npm_available:
        print("⚠️  npm non disponible - Next.js ne sera pas lancé")
        print("   Lancement de Gradio uniquement...\n")
        launch_gradio()
        return
    
    # Lancer l'API pour Next.js
    api_process = None
    if Path("api_server.py").exists():
        print("📡 Démarrage du serveur API Python (port 8000)...")
        try:
            api_process = subprocess.Popen(
                [sys.executable, "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Erreur lors du démarrage de l'API: {e}")
            print("   Continuons avec Gradio uniquement...")
            launch_gradio()
            return
    
    # Lancer Next.js en arrière-plan
    nextjs_process = None
    web_app_path = Path("web-app")
    if web_app_path.exists():
        node_modules = web_app_path / "node_modules"
        if not node_modules.exists():
            print("⚠️  Installation des dépendances Next.js...")
            try:
                subprocess.run(["npm", "install"], cwd=str(web_app_path), check=False)
            except FileNotFoundError:
                print("❌ npm non trouvé")
        
        print("🌐 Démarrage de Next.js (port 3000)...")
        try:
            nextjs_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(web_app_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(3)
        except FileNotFoundError:
            print("⚠️  npm non trouvé - Next.js ne sera pas lancé")
        except Exception as e:
            print(f"⚠️  Erreur lors du démarrage de Next.js: {e}")
    
    # Lancer Gradio au premier plan
    print("🎨 Démarrage de Gradio (port 7860)...")
    print("\n   Interfaces disponibles:")
    print("   - Gradio: http://localhost:7860")
    if nextjs_process and web_app_path.exists():
        print("   - Next.js: http://localhost:3000")
    print("   (Appuyez sur Ctrl+C pour tout arrêter)\n")
    
    try:
        subprocess.run([sys.executable, "client.py"], check=False)
    except KeyboardInterrupt:
        print("\n\n✓ Arrêt de toutes les interfaces...")
    finally:
        if api_process and api_process.poll() is None:
            api_process.terminate()
        if nextjs_process and nextjs_process.poll() is None:
            nextjs_process.terminate()

def main():
    """Fonction principale."""
    print("\n" + "="*70)
    print("  SENTIMENT ANALYSIS WITH FHE - SCRIPT COMPLET")
    print("="*70)
    
    # 1. Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Veuillez installer les dépendances manquantes")
        sys.exit(1)
    
    # 2. Entraîner le modèle
    if not train_model():
        print("\n❌ Échec de l'entraînement. Arrêt du script.")
        sys.exit(1)
    
    # 3. Tester le modèle
    test_model()
    
    # 4. Lancer l'application
    print("\n" + "="*70)
    print("  PRÊT POUR LES TESTS!")
    print("="*70)
    launch_app()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrompu par l'utilisateur")
        sys.exit(0)

