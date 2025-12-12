"""Test script to verify model quality with various phrases."""

from text_processor import TextProcessor
import pickle
from pathlib import Path
import numpy as np

# Load model and processor
print("Chargement du processeur de texte...")
processor = TextProcessor()

model_path = Path('models/sentiment_fhe_model/model_with_simulator.pkl')
if not model_path.exists():
    print(f"ERREUR: Modèle non trouvé à {model_path}")
    print("Veuillez d'abord entraîner le modèle avec: python train_model_simple.py")
    exit(1)

print(f"Chargement du modèle depuis {model_path}...")
with open(model_path, 'rb') as f:
    model = pickle.load(f)

print("✓ Modèle chargé avec succès\n")

# Test phrases
test_phrases = [
    'This is terrible. I am very disappointed.',
    'I love this product! It is amazing!',
    'This is okay, nothing special.',
    'Waste of money. Do not buy it.',
    'The best purchase I have ever made!',
    'So bad, worst product ever.',
    'Excellent quality, highly recommended!',
    'Not worth the price.',
    'Perfect! Exactly what I needed.',
    'Disappointing, expected much better.'
]

print('='*60)
print('MODEL QUALITY TEST')
print('='*60)
print()

correct_predictions = 0
total = len(test_phrases)

for phrase in test_phrases:
    try:
        # Convert text to vector
        X = processor.text_to_tensor([phrase])
        
        # Verify X is not empty
        if X.shape[0] == 0 or X.shape[1] == 0:
            print(f"ERREUR: Vecteur vide pour: {phrase}")
            continue
        
        # Predict
        pred = model.predict(X)
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)
        else:
            print(f"ATTENTION: Le modèle n'a pas de méthode predict_proba")
            proba = None
        
        # Convert prediction to sentiment
        pred_value = int(pred[0]) if isinstance(pred, np.ndarray) else int(pred)
        sentiment = 'Positive' if pred_value == 1 else 'Negative'
        
        if proba is not None and len(proba) > 0 and len(proba[0]) >= 2:
            proba_negative = float(proba[0][0]) * 100
            proba_positive = float(proba[0][1]) * 100
            confidence = max(proba_negative, proba_positive)
        else:
            proba_negative = 50.0
            proba_positive = 50.0
            confidence = 50.0
            print(f"ATTENTION: Probabilités non disponibles, utilisation de valeurs par défaut")
        
        # Expected sentiment (manual check)
        expected = None
        if any(word in phrase.lower() for word in ['terrible', 'disappointed', 'waste', 'bad', 'worst', 'not worth', 'disappointing']):
            expected = 'Negative'
        elif any(word in phrase.lower() for word in ['love', 'amazing', 'best', 'excellent', 'perfect', 'recommended']):
            expected = 'Positive'
        
        is_correct = (expected is None) or (sentiment == expected)
        if is_correct:
            correct_predictions += 1
        
        status = 'OK' if is_correct else 'ERROR'
        if expected is None:
            status = '?'
        
        print(f'{status} Text: "{phrase}"')
        print(f'   Prediction: {sentiment} (confidence: {confidence:.1f}%)')
        if proba is not None:
            print(f'   Probabilities: Negative={proba_negative:.1f}%, Positive={proba_positive:.1f}%')
        if expected is not None:
            print(f'   Expected: {expected}')
        print()
        
    except Exception as e:
        print(f'ERREUR pour "{phrase}": {e}')
        import traceback
        traceback.print_exc()
        print()

print('='*60)
print(f'Results: {correct_predictions}/{total} correct predictions')
print(f'Accuracy: {correct_predictions/total*100:.1f}%')
print('='*60)

