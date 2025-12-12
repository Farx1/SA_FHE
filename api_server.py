"""
Simple API server for sentiment analysis.
Can be called from Next.js application.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js

# Global variables for model and processor
processor = None
model_api = None
model_loaded = False

def load_model():
    """Load model and processor once at startup."""
    global processor, model_api, model_loaded
    
    if model_loaded:
        return
    
    try:
        from text_processor import TextProcessor
        import pickle
        from pathlib import Path
        
        # Load processor
        processor_path = Path("models/text_processor.pkl")
        if processor_path.exists():
            with open(processor_path, "rb") as f:
                processor = pickle.load(f)
        else:
            processor = TextProcessor()
        
        # Load model
        model_path_simulator = Path("models/sentiment_fhe_model/model_with_simulator.pkl")
        if model_path_simulator.exists():
            with open(model_path_simulator, "rb") as f:
                model_api = pickle.load(f)
            model_loaded = True
            print("Model loaded successfully")
        else:
            print("WARNING: Model not found")
            model_loaded = False
            
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        model_loaded = False

# Load model at startup
load_model()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model_loaded
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze sentiment of text."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not isinstance(text, str):
            return jsonify({'error': 'Text is required'}), 400
        
        if not model_loaded or processor is None or model_api is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Process text
        import time
        start = time.time()
        
        # Convert text to vector
        X = processor.text_to_tensor([text])
        
        # Predict
        prediction = model_api.predict(X)
        proba = model_api.predict_proba(X) if hasattr(model_api, 'predict_proba') else None
        
        processing_time = time.time() - start
        
        # Format response
        sentiment_idx = int(prediction[0])
        sentiment = 'Positive' if sentiment_idx == 1 else 'Negative'
        
        if proba is not None:
            proba_negative = float(proba[0][0])
            proba_positive = float(proba[0][1])
            confidence = max(proba_negative, proba_positive) * 100
        else:
            proba_negative = 0.5
            proba_positive = 0.5
            confidence = 50.0
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence,
            'proba_negative': proba_negative,
            'proba_positive': proba_positive,
            'processing_time': processing_time
        })
        
    except Exception as e:
        print(f"Error analyzing text: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting API server...")
    print("Model loaded:", model_loaded)
    app.run(host='0.0.0.0', port=8000, debug=False)

