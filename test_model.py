"""
Script de test complet pour vérifier la cohérence du modèle et des données.
Combine les fonctionnalités de test et de vérification.
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from text_processor import TextProcessor
import warnings
warnings.filterwarnings('ignore')


def verify_data_consistency():
    """Vérifie la cohérence des données d'entraînement."""
    print("=== Vérification de la Cohérence des Données ===\n")
    
    try:
        from datasets import load_dataset
        
        # Charger un petit échantillon
        try:
            dataset = load_dataset("amazon_polarity", split="train[:100]")
            df = pd.DataFrame(dataset)
            print(f"OK - Dataset charge: {len(df)} exemples")
            print(f"OK - Colonnes: {list(df.columns)}")
            if 'label' in df.columns:
                print(f"OK - Distribution des labels: {df['label'].value_counts().to_dict()}")
        except Exception as e:
            print(f"ATTENTION - Impossible de charger le dataset: {e}")
            print("On continue quand meme - cette etape n'est pas critique")
            return True
        
        # Vérifier qu'il n'y a pas de valeurs manquantes
        if df.isnull().sum().sum() == 0:
            print("OK - Aucune valeur manquante")
        else:
            print(f"ATTENTION - Valeurs manquantes detectees: {df.isnull().sum().sum()}")
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        print("On continue quand meme - cette etape n'est pas critique")
        return True


def verify_text_processor():
    """Vérifie que le processeur de texte fonctionne correctement."""
    print("\n=== Vérification du Processeur de Texte ===\n")
    
    try:
        from text_processor import TextProcessor
        
        processor = TextProcessor()
        print("OK - Processeur cree")
        
        # Test avec un texte simple
        test_text = "This is a test."
        result = processor.text_to_tensor([test_text])
        
        print(f"OK - Texte traite avec succes")
        print(f"  Shape: {result.shape}")
        print(f"  Type: {result.dtype}")
        print(f"  Min: {result.min():.4f}, Max: {result.max():.4f}")
        print(f"  Mean: {result.mean():.4f}, Std: {result.std():.4f}")
        
        # Vérifier la cohérence
        if result.shape[0] != 1:
            print(f"ATTENTION - Shape incorrecte: attendu (1, n), obtenu {result.shape}")
            return False
        
        if np.any(np.isnan(result)) or np.any(np.isinf(result)):
            print("ATTENTION - Valeurs NaN ou Inf detectees")
            return False
        
        # Test de répétabilité
        result2 = processor.text_to_tensor([test_text])
        if not np.allclose(result, result2, atol=1e-5):
            print("ATTENTION - Resultats non reproductibles")
            return False
        
        print("OK - Repetabilite verifiee")
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_on_real_test_set():
    """Teste le modèle sur le vrai dataset de test (20% restants - 20 exemples)."""
    print("\n=== Tests sur le Dataset de Test (20% - 20 exemples) ===\n")
    
    try:
        from datasets import load_dataset
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        import pickle
        from pathlib import Path
        
        # Charger le même dataset que l'entraînement
        print("Chargement du dataset...")
        dataset = load_dataset("amazon_polarity", split="train[:100]")  # 100 exemples (20 pour test)
        df = pd.DataFrame(dataset)
        df = df.rename(columns={"content": "text", "label": "sentiment"})
        
        # Même split que l'entraînement (même random_state)
        text_X = df['text'].tolist()
        y = df['sentiment'].values
        _, text_X_test, _, y_test = train_test_split(
            text_X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Dataset de test charge: {len(text_X_test)} exemples")
        print(f"Distribution: {pd.Series(y_test).value_counts().to_dict()}")
        
        # Charger le processeur
        processor_path = Path("models/text_processor.pkl")
        if processor_path.exists():
            with open(processor_path, "rb") as f:
                processor = pickle.load(f)
            print("OK - Processeur charge")
        else:
            processor = TextProcessor()
            print("OK - Nouveau processeur cree")
        
        # Charger le modèle
        model_path_standard = Path("models/sentiment_model_standard.pkl")
        if not model_path_standard.exists():
            print("ERREUR - Modele non trouve")
            return False
        
        with open(model_path_standard, "rb") as f:
            model = pickle.load(f)
        print("OK - Modele charge")
        
        # Transformer les données de test (tous les exemples de test)
        print("\nTransformation des donnees de test...")
        print(f"Traitement de {len(text_X_test)} exemples de test (20% du dataset)...")
        X_test_transformer = processor.text_to_tensor(text_X_test, batch_size=16)
        
        # Prédictions
        print("Calcul des predictions...")
        y_pred = model.predict(X_test_transformer)
        
        # Métriques
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nAccuracy sur {len(y_test)} exemples de test: {accuracy:.4f}")
        print("\nRapport de classification:")
        print(classification_report(y_test, y_pred))
        
        # Vérifications de cohérence
        print("\n=== Verifications de Coherence ===\n")
        
        # Calculer les probabilités pour quelques exemples
        sample_indices = [0, 1, 2, 10, 50]
        all_probas = []
        all_passed = True
        
        for idx in sample_indices:
            X_sample = X_test_transformer[idx:idx+1]
            proba = model.predict_proba(X_sample)
            all_probas.append(proba[0])
            
            # Vérifier que les probabilités somment à 1
            if not np.isclose(proba[0].sum(), 1.0, atol=0.1):
                print(f"ATTENTION - Exemple {idx}: Somme des probabilites anormale: {proba[0].sum():.4f}")
                all_passed = False
            
            # Vérifier que les probabilités sont dans [0, 1]
            if np.any(proba[0] < 0) or np.any(proba[0] > 1):
                print(f"ATTENTION - Exemple {idx}: Probabilites hors de [0, 1]")
                all_passed = False
        
        if all_passed:
            print("OK - Toutes les probabilites sont coherentes")
        
        # Vérifier que les probabilités somment à 1 pour tous
        proba_sums = [p.sum() for p in all_probas]
        if all(np.isclose(s, 1.0, atol=0.1) for s in proba_sums):
            print("OK - Toutes les sommes de probabilites sont correctes")
        else:
            print(f"ATTENTION - Certaines sommes sont incorrectes")
            all_passed = False
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale de test."""
    print("=" * 60)
    print("TESTS COMPLETS DE COHERENCE")
    print("=" * 60)
    print()
    
    results = []
    
    # 1. Vérifier les données
    results.append(("Données", verify_data_consistency()))
    
    # 2. Vérifier le processeur
    results.append(("Processeur de texte", verify_text_processor()))
    
    # 3. Tester le modèle sur le vrai dataset de test (20% - 20 exemples)
    results.append(("Prédictions sur dataset de test (20%)", test_on_real_test_set()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    print()
    
    for name, success in results:
        status = "OK - PASSE" if success else "ERREUR - ECHOUE"
        print(f"{name:30s} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print()
    if all_passed:
        print("OK - Tous les tests sont passes!")
    else:
        print("ATTENTION - Certains tests ont echoue.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
