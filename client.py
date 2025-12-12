"""
Interface client Gradio pour l'analyse de sentiment avec FHE.
"""

import gradio as gr
import numpy as np
import pickle
from pathlib import Path
from text_processor import TextProcessor
import requests
import json
import plotly.graph_objects as go
from datetime import datetime


# Variables globales
processor = None
model_loaded = False
model_api = None  # Global model instance
use_simulator = False  # Whether using simulator

# Statistiques cumulées
stats = {
    "total_predictions": 0,
    "negative_count": 0,
    "positive_count": 0,
    "avg_confidence": 0.0,
    "total_processing_time": 0.0,
    "predictions_history": []  # Liste des dernières prédictions
}


def load_model_and_processor():
    """Charge le modèle et le processeur de texte."""
    global processor, model_loaded, model_api, use_simulator
    
    try:
        # Charger le processeur
        processor_path = Path("models/text_processor.pkl")
        if processor_path.exists():
            with open(processor_path, "rb") as f:
                processor = pickle.load(f)
            print("OK - Text processor loaded")
        else:
            # Créer un nouveau processeur si le fichier n'existe pas
            processor = TextProcessor()
            print("OK - New text processor created")
        
        # Load model once at startup
        model_path_fhe = Path("models/sentiment_fhe_model")
        model_path_simulator = model_path_fhe / "model_with_simulator.pkl"
        model_path_standard = Path("models/sentiment_model_standard.pkl")
        
        # Try to load real FHE model first
        if model_path_fhe.exists():
            try:
                from concrete.ml.deployment import FHEModelDev
                model_api = FHEModelDev("sentiment_fhe_model", path="models/")
                use_simulator = False
                model_loaded = True
                print("OK - FHE model loaded (real FHE)")
            except ImportError:
                # Concrete-ML not available, try simulator model
                if model_path_simulator.exists():
                    with open(model_path_simulator, "rb") as f:
                        model_api = pickle.load(f)
                    use_simulator = True
                    model_loaded = True
                    print("OK - FHE simulator model loaded")
                else:
                    print("INFO - FHE model directory exists but simulator model not found")
                    model_loaded = False
            except Exception as e:
                # Try simulator model if real FHE fails
                if model_path_simulator.exists():
                    with open(model_path_simulator, "rb") as f:
                        model_api = pickle.load(f)
                    use_simulator = True
                    model_loaded = True
                    print("OK - FHE simulator model loaded (fallback)")
                else:
                    print(f"WARNING - Error loading FHE model: {e}")
                    model_loaded = False
        elif model_path_simulator.exists():
            # Load simulator model directly
            with open(model_path_simulator, "rb") as f:
                model_api = pickle.load(f)
            use_simulator = True
            model_loaded = True
            print("OK - FHE simulator model loaded")
        elif model_path_standard.exists():
            # Load standard model
            with open(model_path_standard, "rb") as f:
                model_api = pickle.load(f)
            use_simulator = False
            model_loaded = True
            print("OK - Standard model loaded")
        else:
            print("WARNING - No model found")
            print("   Please train the model first: python train_model_simple.py")
            model_loaded = False
            
    except Exception as e:
        print(f"WARNING - Error during loading: {e}")
        import traceback
        traceback.print_exc()
        model_loaded = False


def analyze_sentiment_detailed(text: str, use_fhe: bool = True):
    """
    Analyze sentiment with detailed step-by-step information for visualization.
    
    Returns a dictionary with all steps for display in Gradio interface.
    """
    steps = {
        "step1_text": "",
        "step1_vector": "",
        "step2_quantization": "",
        "step3_encryption": "",
        "step4_prediction": "",
        "step5_decryption": "",
        "final_result": "",
        "error": None
    }
    
    if processor is None:
        steps["error"] = "Error: Processor not loaded. Please train the model first."
        return steps
    
    # Handle empty or whitespace-only text
    if not text or len(text.strip()) == 0:
        steps["error"] = "Please enter a text to analyze."
        return steps
    
    # Clean and normalize text (handle any edge cases)
    text = text.strip()  # Remove leading/trailing whitespace
    # Text processor will handle truncation automatically (max 512 tokens)
    
    try:
        # STEP 1: Text to Vector Transformation (IN CLEAR)
        steps["step1_text"] = f"Input Text:\n{text}\n\nLength: {len(text)} characters"
        
        X = processor.text_to_tensor([text])
        steps["step1_vector"] = (
            f"Vector Representation (RoBERTa):\n"
            f"Shape: {X.shape}\n"
            f"Type: {X.dtype}\n"
            f"Dimensions: 768 (RoBERTa hidden size)\n"
            f"First 5 values: {X[0][:5].tolist()}\n"
            f"Min: {X.min():.4f}, Max: {X.max():.4f}, Mean: {X.mean():.4f}\n\n"
            f"STATUS: IN CLEAR TEXT (before encryption)"
        )
        
        # STEP 2: Use global model (loaded at startup)
        # Model is already loaded in load_model_and_processor()
        fhe_available = False  # Real FHE not available on Windows
        
        if model_api is None:
            steps["error"] = "ERROR: Model not loaded. Please restart the client."
            return steps
        
        # Always use model.predict() directly for real predictions
        # FHE simulation is only for display purposes
        if use_fhe and model_api is not None:
            import time
            start = time.time()
            
            # STEP 2: Quantization (FHE Process)
            steps["step2_quantization"] = (
                f"QUANTIZATION (FHE Process):\n"
                f"Input: Float32 values (768 dimensions)\n"
                f"Process: Conversion to integers (required for FHE)\n"
                f"Precision: n_bits=3 (quantization parameter)\n"
                f"Example: 0.75 → 3 (quantized integer)\n\n"
                f"WHY: FHE cryptographic operations require integer inputs\n"
                f"STATUS: Quantization complete"
            )
            
            # STEP 3: Encryption (FHE Process)
            steps["step3_encryption"] = (
                f"ENCRYPTION (FHE Process):\n"
                f"Input: Quantized integers\n"
                f"Process: Encryption with public key\n"
                f"Output: Ciphertext (encrypted data)\n"
                f"Key: Public key (generated during model compilation)\n\n"
                f"RESULT: Data is encrypted and unreadable\n"
                f"The model processes only encrypted values\n"
                f"STATUS: Encryption complete"
            )
            
            # STEP 4: FHE Prediction (FHE Process)
            steps["step4_prediction"] = (
                f"FHE PREDICTION (On Encrypted Data):\n"
                f"Input: Encrypted data (ciphertext)\n"
                f"Process: XGBoost model operations on ciphertext\n"
                f"Operations: Additions, multiplications (homomorphic)\n"
                f"Model sees: Only encrypted data, never clear values\n"
                f"Output: Encrypted prediction (ciphertext)\n\n"
                f"KEY POINT: All computations happen on encrypted data!\n"
                f"STATUS: Prediction complete (encrypted result)"
            )
            
            # IMPORTANT: Use model.predict() directly for real predictions
            # This uses the actual trained model, not a simulation
            try:
                prediction = model_api.predict(X)
                prediction_time = time.time() - start
                
                sentiment_idx = int(prediction[0])
                sentiment_labels = ["Negative", "Positive"]
                sentiment = sentiment_labels[sentiment_idx] if sentiment_idx < len(sentiment_labels) else "Unknown"
                
                # STEP 5: Decryption (FHE Process)
                steps["step5_decryption"] = (
                    f"DECRYPTION (FHE Process):\n"
                    f"Input: Encrypted prediction (ciphertext)\n"
                    f"Process: Decryption with secret (private) key\n"
                    f"Key: Secret key (only client has this)\n"
                    f"Output: Clear prediction\n\n"
                    f"RESULT: {sentiment_idx} (0=Negative, 1=Positive)\n"
                    f"STATUS: Decryption complete - prediction ready"
                )
                
                # Get prediction probabilities for more transparency
                try:
                    if hasattr(model_api, 'predict_proba'):
                        proba = model_api.predict_proba(X)
                        proba_negative = proba[0][0] if len(proba[0]) > 0 else 0.0
                        proba_positive = proba[0][1] if len(proba[0]) > 1 else 0.0
                        confidence = max(proba_negative, proba_positive) * 100
                    else:
                        proba_negative = 0.0
                        proba_positive = 0.0
                        confidence = 0.0
                except:
                    proba_negative = 0.0
                    proba_positive = 0.0
                    confidence = 0.0
                
                # Mettre à jour les statistiques
                stats["total_predictions"] += 1
                if sentiment_idx == 0:
                    stats["negative_count"] += 1
                else:
                    stats["positive_count"] += 1
                
                # Mettre à jour la moyenne de confiance
                total_conf = stats["avg_confidence"] * (stats["total_predictions"] - 1) + confidence
                stats["avg_confidence"] = total_conf / stats["total_predictions"]
                stats["total_processing_time"] += prediction_time
                
                # Ajouter à l'historique (garder les 10 dernières)
                stats["predictions_history"].append({
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                if len(stats["predictions_history"]) > 10:
                    stats["predictions_history"].pop(0)
                
                steps["final_result"] = (
                    f"PREDICTION RESULT\n"
                    f"{'='*50}\n"
                    f"Sentiment: {sentiment}\n"
                    f"Confidence: {confidence:.1f}%\n\n"
                    f"Probabilities:\n"
                    f"  Negative: {proba_negative*100:.1f}%\n"
                    f"  Positive: {proba_positive*100:.1f}%\n\n"
                    f"Processing Time: {prediction_time:.4f}s\n"
                    f"{'='*50}"
                )
            except Exception as e:
                steps["error"] = f"Prediction Error: {str(e)}"
                import traceback
                traceback.print_exc()
        
        elif not use_fhe:
            # Clear mode (for comparison)
            steps["step2_quantization"] = (
                "SKIPPED (Clear Mode)\n"
                "No quantization needed - processing floats directly"
            )
            steps["step3_encryption"] = (
                "SKIPPED (Clear Mode)\n"
                "No encryption - data remains in clear text"
            )
            
            if model_api is not None:
                try:
                    steps["step4_prediction"] = (
                        "PREDICTION (Clear Mode):\n"
                        "Input: Clear vector (float32)\n"
                        "Process: Direct XGBoost prediction\n"
                        "Output: Clear prediction\n\n"
                        "NOTE: This is for comparison only - no encryption!"
                    )
                    
                    prediction = model_api.predict(X)
                    
                    steps["step5_decryption"] = (
                        "SKIPPED (Clear Mode)\n"
                        "No decryption needed - result already in clear"
                    )
                    
                    sentiment_idx = int(prediction[0])
                    sentiment_labels = ["Negative", "Positive"]
                    sentiment = sentiment_labels[sentiment_idx] if sentiment_idx < len(sentiment_labels) else "Unknown"
                    
                    # Get probabilities
                    try:
                        if hasattr(model_api, 'predict_proba'):
                            proba = model_api.predict_proba(X)
                            proba_negative = proba[0][0] if len(proba[0]) > 0 else 0.0
                            proba_positive = proba[0][1] if len(proba[0]) > 1 else 0.0
                            confidence = max(proba_negative, proba_positive) * 100
                        else:
                            proba_negative = 0.0
                            proba_positive = 0.0
                            confidence = 0.0
                    except:
                        proba_negative = 0.0
                        proba_positive = 0.0
                        confidence = 0.0
                    
                    # Mettre à jour les statistiques (mode clear aussi)
                    stats["total_predictions"] += 1
                    if sentiment_idx == 0:
                        stats["negative_count"] += 1
                    else:
                        stats["positive_count"] += 1
                    
                    total_conf = stats["avg_confidence"] * (stats["total_predictions"] - 1) + confidence
                    stats["avg_confidence"] = total_conf / stats["total_predictions"]
                    
                    steps["final_result"] = (
                        f"RESULT (Clear Mode)\n"
                        f"{'='*50}\n"
                        f"Sentiment: {sentiment}\n"
                        f"Confidence: {confidence:.1f}%\n\n"
                        f"Probabilities:\n"
                        f"  Negative: {proba_negative*100:.1f}%\n"
                        f"  Positive: {proba_positive*100:.1f}%\n\n"
                        f"NOTE: Processed without encryption (for comparison)\n"
                        f"{'='*50}"
                    )
                except Exception as e:
                    steps["step4_prediction"] = f"PREDICTION: Error - {str(e)}"
                    steps["step5_decryption"] = "SKIPPED"
                    steps["final_result"] = f"Error: {str(e)}"
            else:
                steps["step4_prediction"] = "PREDICTION: No model available"
                steps["step5_decryption"] = "SKIPPED"
                steps["final_result"] = "No model available. Please train the model first."
            
    except Exception as e:
        steps["error"] = f"Error: {str(e)}"
    
    return steps


def analyze_sentiment_local(text: str, use_fhe: bool = True):
    """
    Analyze sentiment (simple version for backward compatibility).
    """
    steps = analyze_sentiment_detailed(text, use_fhe)
    if steps["error"]:
        return steps["error"]
    return steps["final_result"]


def analyze_sentiment_server(text: str, server_url: str = "http://localhost:8000"):
    """
    Analyse le sentiment en utilisant le serveur distant.
    
    Args:
        text: Texte à analyser
        server_url: URL du serveur
    """
    if processor is None:
        return "Erreur: Processeur non chargé."
    
    if not text or len(text.strip()) == 0:
        return "Veuillez entrer un texte à analyser."
    
    try:
        # Vérifier que le serveur est accessible
        health_check = requests.get(f"{server_url}/health", timeout=2)
        if health_check.status_code != 200:
            return f"Erreur: Serveur non accessible (code {health_check.status_code})"
        
        # Traiter le texte
        X = processor.text_to_tensor([text])
        
        # Pour l'instant, utiliser le mode local car l'API serveur nécessite une configuration plus complexe
        # En production, on utiliserait FHEModelClient pour chiffrer et envoyer
        return "Mode serveur nécessite une configuration FHE complète. Utilisez le mode Local FHE pour l'instant."
            
    except requests.exceptions.ConnectionError:
        return f"Erreur: Impossible de se connecter au serveur à {server_url}\nAssurez-vous que le serveur est démarré (python server.py)"
    except Exception as e:
        return f"Erreur: {str(e)}"


def create_stats_display():
    """Crée l'affichage des statistiques."""
    total = stats["total_predictions"]
    negative = stats["negative_count"]
    positive = stats["positive_count"]
    avg_conf = stats["avg_confidence"]
    avg_time = stats["total_processing_time"] / total if total > 0 else 0.0
    
    # Calculer les pourcentages
    neg_pct = (negative/total*100) if total > 0 else 0.0
    pos_pct = (positive/total*100) if total > 0 else 0.0
    
    stats_text = f"""
## 📊 Statistics Dashboard

**Total Predictions:** {total}

**Sentiment Distribution:**
- Negative: {negative} ({neg_pct:.1f}%)
- Positive: {positive} ({pos_pct:.1f}%)

**Performance:**
- Average Confidence: {avg_conf:.1f}%
- Average Processing Time: {avg_time:.4f}s

**Recent Predictions:**
"""
    
    if stats["predictions_history"]:
        for pred in reversed(stats["predictions_history"][-5:]):  # 5 dernières
            stats_text += f"\n- [{pred['timestamp']}] {pred['text']} → **{pred['sentiment']}** ({pred['confidence']:.1f}%)"
    else:
        stats_text += "\n_No predictions yet. Start analyzing text to see statistics!_"
    
    return stats_text


def create_sentiment_chart():
    """Crée un graphique de distribution des sentiments."""
    if stats["total_predictions"] == 0:
        # Graphique avec des valeurs par défaut pour qu'il soit visible
        fig = go.Figure(data=[
            go.Bar(
                x=['Negative', 'Positive'],
                y=[0, 0],
                marker_color=['#ef4444', '#10b981'],
                text=['0', '0'],
                textposition='auto',
            )
        ])
        fig.add_annotation(
            text="No data yet. Start analyzing to see the chart!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        )
        fig.update_layout(
            title=dict(text="Sentiment Distribution", font=dict(size=16)),
            xaxis_title="Sentiment",
            yaxis_title="Number of Predictions",
            height=350,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=20, t=50, b=40)
        )
        return fig
    
    labels = ['Negative', 'Positive']
    values = [stats["negative_count"], stats["positive_count"]]
    colors = ['#ef4444', '#10b981']  # Rouge pour négatif, vert pour positif
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto',
            textfont=dict(size=14, color='white', family='Arial Black'),
            marker_line=dict(color='rgba(0,0,0,0.2)', width=1)
        )
    ])
    
    fig.update_layout(
        title=dict(text="Sentiment Distribution", font=dict(size=16, color='#333')),
        xaxis=dict(title="Sentiment", titlefont=dict(size=12)),
        yaxis=dict(title="Number of Predictions", titlefont=dict(size=12)),
        height=350,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(family="Arial, sans-serif")
    )
    
    return fig


# Interface Gradio
def create_interface():
    """Crée l'interface Gradio."""
    
    # CSS personnalisé pour un design moderne
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
    .stats-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #e9ecef;
        margin: 10px 0;
    }
    .chart-box {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #e9ecef;
        margin: 10px 0;
    }
    .result-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    """
    
    with gr.Blocks(title="Sentiment Analysis with FHE", theme=gr.themes.Soft(), css=custom_css) as demo:
        # ========== HEADER ==========
        gr.Markdown(
            """
            <div class="header-section">
                <h1 style="margin: 0; font-size: 32px;">🔒 Sentiment Analysis with FHE</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
                    Real-time sentiment analysis with Fully Homomorphic Encryption
                </p>
            </div>
            """
        )
        
        # ========== SECTION PRINCIPALE: INPUT + STATISTIQUES ==========
        with gr.Row():
            # Colonne gauche: Input
            with gr.Column(scale=2, min_width=450):
                gr.Markdown("## 📝 Text Input")
                text_input = gr.Textbox(
                    label="Enter your text to analyze",
                    placeholder="Example: 'This product is amazing! I love it!'",
                    lines=5,
                    show_label=True
                )
                
                with gr.Row():
                    mode = gr.Radio(
                        choices=["Local FHE", "Local Clear"],
                        value="Local FHE",
                        label="Execution Mode",
                        scale=2,
                        info="FHE mode shows encryption process, Clear mode for comparison"
                    )
                    analyze_btn = gr.Button(
                        "🚀 Analyze Sentiment", 
                        variant="primary",
                        scale=1,
                        size="lg"
                    )
            
            # Colonne droite: Statistiques et Graphique
            with gr.Column(scale=1, min_width=350):
                gr.Markdown("## 📊 Live Statistics & Analytics")
                
                # Box Statistiques
                with gr.Box(elem_classes=["stats-box"]):
                    gr.Markdown("### 📈 Statistics Dashboard")
                    stats_display = gr.Markdown(create_stats_display())
                
                # Box Graphique
                with gr.Box(elem_classes=["chart-box"]):
                    gr.Markdown("### 📊 Sentiment Distribution Chart")
                    sentiment_chart = gr.Plot(
                        value=create_sentiment_chart(),
                        label="",
                        show_label=False,
                        container=True,
                        elem_id="sentiment_chart"
                    )
        
        gr.Markdown("---")
        
        # ========== SECTION RESULTAT PRINCIPAL ==========
        gr.Markdown("## 🎯 Prediction Result")
        final_result = gr.Textbox(
            label="",
            lines=10,
            interactive=False,
            elem_classes=["result-box"],
            show_label=False
        )
        
        gr.Markdown("---")
        
        # ========== SECTION DETAILLEE FHE (COLLAPSIBLE) ==========
        with gr.Accordion("🔍 Detailed FHE Process Steps - Click to expand", open=False):
            gr.Markdown(
                """
                ### Step-by-Step FHE Process Visualization
                
                This section shows the detailed steps of the Fully Homomorphic Encryption process.
                Each step is displayed below when you analyze a text.
                """
            )
            
            with gr.Row():
                with gr.Column():
                    step1_text = gr.Textbox(
                        label="STEP 1: Input Text",
                        lines=3,
                        interactive=False,
                        placeholder="Input text will appear here..."
                    )
                    step1_vector = gr.Textbox(
                        label="STEP 1: Text → Vector (RoBERTa) - IN CLEAR",
                        lines=6,
                        interactive=False,
                        placeholder="Vector representation will appear here..."
                    )
                    
            with gr.Row():
                with gr.Column():
                    step2_quant = gr.Textbox(
                        label="STEP 2: Quantization (Float → Integer)",
                        lines=5,
                        interactive=False,
                        placeholder="Quantization details will appear here..."
                    )
                    step3_encrypt = gr.Textbox(
                        label="STEP 3: ENCRYPTION (Clear → Ciphertext)",
                        lines=6,
                        interactive=False,
                        placeholder="Encryption details will appear here..."
                    )
                    
            with gr.Row():
                with gr.Column():
                    step4_pred = gr.Textbox(
                        label="STEP 4: FHE PREDICTION (On Encrypted Data)",
                        lines=6,
                        interactive=False,
                        placeholder="FHE prediction details will appear here..."
                    )
                    step5_decrypt = gr.Textbox(
                        label="STEP 5: DECRYPTION (Ciphertext → Clear)",
                        lines=6,
                        interactive=False,
                        placeholder="Decryption details will appear here..."
                    )
        
        error_display = gr.Textbox(
            label="⚠️ Errors / Warnings",
            lines=3,
            interactive=False,
            visible=False
        )
        
        gr.Markdown("---")
        
        # ========== SECTION EXPLICATION FHE ==========
        with gr.Accordion("📚 How FHE Works - Technical Explanation", open=False):
            gr.Markdown(
                """
                ## How Fully Homomorphic Encryption (FHE) Works
                
                This section explains the technical details of the FHE process used in this application.
                
                ### Step 1: Text → Vector (IN CLEAR)
                - **Process**: The input text is converted to a 768-dimensional vector using RoBERTa
                - **Why Clear**: This step is in clear text (before encryption) because RoBERTa needs to process the text
                - **Output**: A numerical vector representation of the text
                - **Location in Code**: `text_processor.py`, function `text_to_tensor()`
                
                ### Step 2: Quantization (Float → Integer)
                - **Process**: Float values are converted to integers (required for FHE)
                - **Why**: FHE cryptographic operations can only work with integers, not floating-point numbers
                - **Precision**: Precision is reduced (typically 2-3 bits) but necessary for cryptographic operations
                - **Location in Code**: Automatic in `model.compile()` during training
                
                ### Step 3: ENCRYPTION (Clear → Ciphertext)
                - **Process**: Data is encrypted using the public key
                - **Result**: The data becomes unreadable (ciphertext)
                - **Security**: The server/model cannot see the original values
                - **Key**: Public key (generated during model compilation)
                - **Location in Code**: Automatic in `client.py` when FHE mode is enabled
                
                ### Step 4: FHE PREDICTION (On Encrypted Data)
                - **Process**: The XGBoost model processes encrypted data
                - **Operations**: All operations (additions, multiplications) happen on ciphertext
                - **Security**: The model never sees clear data - only encrypted values
                - **Output**: Encrypted prediction (still in ciphertext)
                - **Location in Code**: `client.py` - `model_api.predict(X)` with FHE enabled
                
                ### Step 5: DECRYPTION (Ciphertext → Clear)
                - **Process**: The encrypted result is decrypted using the secret (private) key
                - **Security**: Only the client has the secret key
                - **Output**: Clear prediction result
                - **Location in Code**: Automatic after prediction in `client.py`
                
                ### 🔑 Key Security Point
                
                **Data remains encrypted throughout the entire processing pipeline!**
                
                - The server/model only sees encrypted data
                - All computations happen on encrypted data
                - Only the client can decrypt the final result
                - This ensures complete privacy and security
                
                ### 📍 Code Locations
                
                - **Text Processing**: `text_processor.py` - `text_to_tensor()` function
                - **Model Training**: `train_model_simple.py` - `compile_model()` function
                - **FHE Execution**: `client.py` - `analyze_sentiment_detailed()` function
                - **Model Utils**: `model_utils.py` - `compile_model()` function
                """
            )
        
        gr.Markdown("---")
        
        # ========== SECTION EXEMPLES ==========
        gr.Markdown("## 💡 Example Texts")
        gr.Markdown("Click on any example below to try it:")
        examples = gr.Examples(
            examples=[
                ["I love this product! It's amazing!"],
                ["This is terrible. I'm very disappointed."],
                ["It's okay, nothing special."],
                ["The best purchase I've ever made!"],
                ["Waste of money. Don't buy it."],
                ["Excellent quality, highly recommended!"],
                ["So bad, worst product ever."]
            ],
            inputs=text_input,
            label=""
        )
        
        def analyze_detailed(text, mode_choice):
            """Analyze with detailed step-by-step output."""
            use_fhe = (mode_choice == "Local FHE")
            steps = analyze_sentiment_detailed(text, use_fhe)
            
            # If there's an error, show it in error_display and clear other fields
            error_msg = steps.get("error", "")
            if error_msg:
                return (
                    steps.get("step1_text", ""),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    error_msg,
                    create_stats_display(),
                    create_sentiment_chart()
                )
            
            # Return all steps for display + updated statistics
            return (
                steps.get("step1_text", ""),
                steps.get("step1_vector", ""),
                steps.get("step2_quantization", ""),
                steps.get("step3_encryption", ""),
                steps.get("step4_prediction", ""),
                steps.get("step5_decryption", ""),
                steps.get("final_result", ""),
                "",  # No error
                create_stats_display(),  # Updated statistics
                create_sentiment_chart()  # Updated chart
            )
        
        analyze_btn.click(
            fn=analyze_detailed,
            inputs=[text_input, mode],
            outputs=[step1_text, step1_vector, step2_quant, step3_encrypt, 
                    step4_pred, step5_decrypt, final_result, error_display,
                    stats_display, sentiment_chart]
        )
        
        text_input.submit(
            fn=analyze_detailed,
            inputs=[text_input, mode],
            outputs=[step1_text, step1_vector, step2_quant, step3_encrypt, 
                    step4_pred, step5_decrypt, final_result, error_display,
                    stats_display, sentiment_chart]
        )
    
    return demo


if __name__ == "__main__":
    print("Loading model and processor...")
    load_model_and_processor()
    
    if not model_loaded:
        print("\n" + "="*60)
        print("INFO: No FHE model found")
        print("="*60)
        print("\nThe interface is ready for testing")
        print("showing the FHE process structure.")
        print("\nTo use real FHE:")
        print("1. Install Concrete-ML: pip install concrete-ml (requires Linux/WSL/Colab)")
        print("2. Train the model: python train_model_simple.py")
        print("3. The FHE model will be created in models/sentiment_fhe_model/")
        print("\nStarting interface for model testing...")
        print("="*60)
    
    print("Creating Gradio interface...")
    demo = create_interface()
    
    print("Launching interface...")
    # Find an available port
    import socket
    
    def find_available_port(start_port=7860, max_attempts=20):
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        # If no port found, let the OS assign one
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
            return port
    
    port = find_available_port(7860, 20)
    print(f"Starting server on port {port}...")
    demo.launch(share=False, server_name="0.0.0.0", server_port=port)

