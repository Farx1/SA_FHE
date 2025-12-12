"""
Utilitaires pour la gestion du modèle FHE.
Supports both real FHE (Concrete-ML) and simulated FHE (Windows native).
"""

import pickle
import os
from pathlib import Path

# Try to import Concrete-ML, fallback to simulator if not available
try:
    from concrete.ml.sklearn import XGBClassifier
    from concrete.ml.deployment import FHEModelDev
    FHE_AVAILABLE = True
    USE_SIMULATOR = False
except (ImportError, ModuleNotFoundError):
    FHE_AVAILABLE = False
    USE_SIMULATOR = True
    # Import simulator for Windows
    from fhe_simulator import FHESimulator
    # Create dummy classes for type hints
    class XGBClassifier:
        pass
    class FHEModelDev:
        pass


def save_model(model, model_name: str = "sentiment_fhe_model"):
    """
    Save the compiled FHE model.
    
    Saves the model with:
    - The compiled FHE circuit
    - Cryptographic keys (public key, evaluation keys)
    - Quantization parameters
    
    USAGE: Called in train_model_simple.py line 168 after compilation.
    
    Args:
        model: XGBClassifier model compiled (with FHE circuit)
        model_name: Model name for saving
    """
    if not FHE_AVAILABLE:
        raise ImportError("Concrete-ML is not available. Cannot save FHE model.")
    
    os.makedirs("models", exist_ok=True)
    
    # Save FHE model with all its keys
    # FHEModelDev encapsulates the compiled model + cryptographic keys
    fhe_api = FHEModelDev(model_name, model)
    # Saves in models/sentiment_fhe_model/:
    # - The compiled FHE circuit
    # - Cryptographic keys (necessary for encryption/decryption)
    # - Quantization parameters
    fhe_api.save("models/")
    
    # Also save the clear model for reference (optional)
    with open(f"models/{model_name}_clear.pkl", "wb") as f:
        pickle.dump(model, f)
    
    print(f"Model saved in models/{model_name}/")


def load_model(model_name: str = "sentiment_fhe_model"):
    """
    Load a saved FHE model.
    
    Args:
        model_name: Model name to load
        
    Returns:
        Loaded FHEModelDev instance
    """
    if not FHE_AVAILABLE:
        raise ImportError("Concrete-ML is not available. Cannot load FHE model.")
    
    model_path = Path("models") / model_name
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    fhe_api = FHEModelDev(model_name, path=str(model_path.parent))
    return fhe_api


def compile_model(model, X_sample):
    """
    CRITICAL STEP: Compile model for FHE execution.
    
    This function transforms the standard XGBoost model into an FHE cryptographic circuit.
    
    WHAT HAPPENS HERE:
    1. QUANTIZATION: Conversion of float data → integers (necessary for FHE)
       - Float values are rounded and converted to integers
       - Precision is reduced (n_bits, typically 2-3 bits)
       - Example: 0.75 → 3 (if n_bits=2, we have 4 possible values: 0,1,2,3)
    
    2. COMPILATION: Transformation of model into FHE circuit
       - XGBoost model is converted to cryptographic operations
       - Each operation (addition, multiplication) becomes an FHE operation
       - Generation of cryptographic keys (secret key, public key, evaluation keys)
    
    3. FHE CIRCUIT: Creation of executable circuit on encrypted data
       - The circuit can process ciphertexts (encrypted data)
       - Results are also ciphertexts
    
    USAGE: This function is called in train_model_simple.py line 161
           after model training, before saving.
    
    Args:
        model: Trained XGBClassifier model (in float)
        X_sample: Data sample for compilation (used to calibrate quantization)
        
    Returns:
        Compiled model (ready for FHE, with integrated cryptographic circuit)
    """
    if FHE_AVAILABLE and not USE_SIMULATOR:
        # Real FHE with Concrete-ML
        print("Compiling model for FHE (this may take a few minutes)...")
        model.compile(X_sample)
        print("Compilation complete!")
        return model
    else:
        # Simulated FHE for Windows
        print("INFO: Using FHE simulator (Concrete-ML not available on Windows)")
        print("This demonstrates the FHE process structure:")
        print("  1. Quantization (float -> int)")
        print("  2. Encryption (with public key)")
        print("  3. Computation on encrypted data")
        print("  4. Decryption (with secret key)")
        print("  5. Dequantization (int -> float)")
        print("")
        print("NOTE: This is a simulation for educational purposes.")
        print("For real FHE, use Linux/WSL/Colab with Concrete-ML.")
        
        # Create simulator and attach to model
        simulator = FHESimulator(n_bits=3)
        model._fhe_simulator = simulator
        model._fhe_compiled = True
        
        print("FHE simulator initialized (model ready for demonstration)")
        return model

