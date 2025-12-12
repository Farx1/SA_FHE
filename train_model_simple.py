"""
Version simplifiée du script d'entraînement qui fonctionne sans FHE.
Utile pour tester le pipeline avant d'installer Concrete-ML.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from datasets import load_dataset
import time
import warnings
warnings.filterwarnings('ignore')

# Try to import FHE XGBoost, fallback to standard XGBoost
try:
    from concrete.ml.sklearn import XGBClassifier
    FHE_AVAILABLE = True
    USE_SIMULATOR = False
    print("OK - Concrete-ML disponible - FHE active")
except (ImportError, ModuleNotFoundError):
    from xgboost import XGBClassifier
    FHE_AVAILABLE = False
    USE_SIMULATOR = True
    print("INFO - Concrete-ML non disponible")
    print("      Utilisation du simulateur FHE (demonstration educative)")
    print("      Le projet fonctionne en mode demonstration sur Windows")

from text_processor import TextProcessor


def load_and_prepare_data():
    """Charge et prépare le dataset."""
    print("Chargement du dataset...")
    
    try:
        # Utiliser un dataset de reviews Amazon (augmenté pour meilleure qualité)
        # Utiliser 2000 exemples pour un meilleur entraînement
        dataset = load_dataset("amazon_polarity", split="train[:2000]")
        df = pd.DataFrame(dataset)
        df = df.rename(columns={"content": "text", "label": "sentiment"})
        print(f"Dataset chargé: {len(df)} exemples")
        print(f"Distribution des sentiments:\n{df['sentiment'].value_counts()}")
    except Exception as e:
        print(f"Erreur lors du chargement du dataset Amazon: {e}")
        print("Utilisation d'un dataset alternatif (IMDB)...")
        try:
            # Fallback sur IMDB avec plus de données
            dataset = load_dataset("imdb", split="train[:2000]")
            df = pd.DataFrame(dataset)
            df = df.rename(columns={"text": "text", "label": "sentiment"})
            print(f"Dataset IMDB chargé: {len(df)} exemples")
        except Exception as e2:
            print(f"Erreur lors du chargement IMDB: {e2}")
            print("Utilisation d'un dataset minimal...")
            # Dernier recours: dataset minimal
            dataset = load_dataset("imdb", split="train[:500]")
            df = pd.DataFrame(dataset)
            df = df.rename(columns={"text": "text", "label": "sentiment"})
    
    return df


def main():
    """Fonction principale d'entraînement."""
    
    # 1. Charger les données
    df = load_and_prepare_data()
    
    # 2. Préparer les données
    text_X = df['text'].tolist()
    y = df['sentiment'].values
    
    # Split train/test
    text_X_train, text_X_test, y_train, y_test = train_test_split(
        text_X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nDonnées d'entraînement: {len(text_X_train)} exemples")
    print(f"Données de test: {len(text_X_test)} exemples")
    
    # 3. Traiter le texte avec le transformer
    print("\n=== Traitement du texte avec le transformer ===")
    processor = TextProcessor()
    
    print("Transformation des données d'entraînement...")
    X_train_transformer = processor.text_to_tensor(text_X_train, batch_size=16)
    
    print("Transformation des données de test...")
    X_test_transformer = processor.text_to_tensor(text_X_test, batch_size=16)
    
    print(f"Shape des features d'entraînement: {X_train_transformer.shape}")
    print(f"Shape des features de test: {X_test_transformer.shape}")
    
    # 4. Entraîner le modèle XGBoost
    print("\n=== Entraînement du modèle XGBoost ===")
    
    if FHE_AVAILABLE:
        model = XGBClassifier()
        parameters = {
            "n_bits": [3],  # Fixed to 3 for better precision
            "max_depth": [3, 5, 7],
            "n_estimators": [50, 100, 150],
            "learning_rate": [0.1, 0.2],
            "n_jobs": [-1],
        }
    else:
        from xgboost import XGBClassifier
        model = XGBClassifier()
        parameters = {
            "max_depth": [3, 5, 7],
            "n_estimators": [50, 100, 150],
            "learning_rate": [0.1, 0.2],
            "n_jobs": [-1],
        }
    
    print("Recherche des meilleurs hyperparamètres...")
    grid_search = GridSearchCV(
        model, 
        parameters, 
        cv=5,  # Increased CV folds for better validation
        n_jobs=1, 
        scoring="accuracy",
        verbose=1
    )
    
    grid_search.fit(X_train_transformer, y_train)
    
    print(f"\nMeilleur score (CV): {grid_search.best_score_:.4f}")
    print(f"Meilleurs paramètres: {grid_search.best_params_}")
    
    # 5. Évaluer sur le test set
    best_model = grid_search.best_estimator_
    
    print("\n=== Évaluation sur le test set ===")
    y_pred = best_model.predict(X_test_transformer)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy sur le test set: {accuracy:.4f}")
    print("\nRapport de classification:")
    print(classification_report(y_test, y_pred))
    print("\nMatrice de confusion:")
    print(confusion_matrix(y_test, y_pred))
    
    # 6. Tester une prédiction
    print("\n=== Test d'une prédiction ===")
    test_text = ["This product is amazing! I love it!"]
    X_test = processor.text_to_tensor(test_text)
    
    prediction = best_model.predict(X_test)
    proba = best_model.predict_proba(X_test)
    
    sentiment_labels = ["Négatif", "Positif"]
    sentiment = sentiment_labels[int(prediction[0])]
    
    print(f"Texte: {test_text[0]}")
    print(f"Sentiment prédit: {sentiment}")
    print(f"Probabilités: {proba}")
    
    # 7. Sauvegarder le modèle
    print("\n=== Compilation et sauvegarde FHE ===")
    try:
        from model_utils import save_model, compile_model
        
        # CRITICAL STEP: Compile model for FHE (or FHE simulator)
        # This step transforms the standard model into a cryptographic circuit
        # OR initializes the FHE simulator for demonstration
        # 
        # WHAT HAPPENS IN compile_model():
        # 1. Quantization: Conversion float → integers (necessary for FHE)
        # 2. Compilation: Transformation into executable FHE circuit (or simulator)
        # 3. Key generation: Secret key, public key, evaluation keys (or simulated)
        #
        # X_train_transformer[:100] is used as sample to calibrate
        # quantization (determine min/max bounds for each feature)
        start = time.perf_counter()
        best_model = compile_model(best_model, X_train_transformer[:100])
        end = time.perf_counter()
        print(f"Temps de compilation: {end - start:.2f} secondes")
        
        # Save model (with FHE or simulator)
        import pickle
        import os
        os.makedirs("models", exist_ok=True)
        
        if FHE_AVAILABLE and not USE_SIMULATOR:
            # Real FHE - save with Concrete-ML
            save_model(best_model, "sentiment_fhe_model")
            
            # FHE TEST: Verify that encryption works
            start = time.perf_counter()
            fhe_proba = best_model.predict_proba(X_test, execute_in_fhe=True)
            end = time.perf_counter()
            print(f"Probabilités (FHE): {fhe_proba}")
            print(f"Temps d'inférence FHE: {end - start:.2f} secondes")
        else:
            # Simulator mode - save with simulator
            from pathlib import Path
            model_path = Path("models/sentiment_fhe_model")
            model_path.mkdir(exist_ok=True)
            with open(model_path / "model_with_simulator.pkl", "wb") as f:
                pickle.dump(best_model, f)
            print(f"Modèle avec simulateur FHE sauvegardé dans {model_path}/")
            print("Le simulateur FHE est prêt pour la démonstration!")
            
    except Exception as e:
        print(f"Erreur lors de la compilation: {e}")
        import traceback
        traceback.print_exc()
    
    # Sauvegarder le processeur
    import pickle
    import os
    os.makedirs("models", exist_ok=True)
    with open("models/text_processor.pkl", "wb") as f:
        pickle.dump(processor, f)
    
    print("\nOK - Entrainement termine avec succes!")


if __name__ == "__main__":
    main()

