"""
Module pour le traitement du texte avec des transformers.
Convertit le texte en représentations vectorielles utilisables par le modèle FHE.
"""

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List
import tqdm


class TextProcessor:
    """Classe pour transformer le texte en représentations vectorielles."""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest", device: str = None):
        """
        Initialise le processeur de texte.
        
        Args:
            model_name: Nom du modèle transformer à utiliser
            device: Device PyTorch ('cuda' ou 'cpu'). Si None, détecte automatiquement.
        """
        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Chargement du modèle {model_name} sur {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()  # Mode évaluation
        
    def text_to_tensor(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        TEXT TO NUMERIC VECTOR TRANSFORMATION (IN CLEAR)
        
        This function converts text into vector representation usable by the ML model.
        
        WHAT HAPPENS:
        1. TOKENIZATION: Text is split into tokens (words/subwords)
        2. ENCODING: Tokens are converted to numeric IDs
        3. ROERTA: Pass through pre-trained RoBERTa model
        4. EXTRACTION: Retrieve hidden states (internal representations)
        5. POOLING: Average representations to get one vector per text
        
        RESULT:
        - Format: Numpy array (n_texts, 768)
        - Type: float32 (real values)
        - Dimensions: 768 (size of RoBERTa hidden layer)
        
        IMPORTANT: This step is IN CLEAR (before FHE encryption)
                   Data will be encrypted later in client.py
        
        USAGE: Called in:
               - train_model_simple.py line 73 (training)
               - client.py line 65 (prediction)
        
        Args:
            texts: Liste de textes à transformer
            batch_size: Taille des batches pour le traitement
            
        Returns:
            Array numpy de shape (n_texts, 768) en float32
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Normalize texts: ensure all are strings and handle edge cases
        normalized_texts = []
        for text in texts:
            if not isinstance(text, str):
                text = str(text)
            # Remove excessive whitespace but keep structure
            text = " ".join(text.split())
            # Ensure text is not empty (use placeholder if needed)
            if len(text.strip()) == 0:
                text = " "  # Single space as placeholder
            normalized_texts.append(text)
        texts = normalized_texts
            
        # STEP 1: TOKENIZATION
        # Splits text into tokens (words/subwords) and converts to numeric IDs
        # Example: "I love this" → [0, 123, 456, 789] (numeric IDs)
        # max_length=512 ensures any text can be processed (longer texts are truncated)
        tokenized_texts = [
            self.tokenizer.encode(text, return_tensors="pt", truncation=True, max_length=512, padding=False)
            for text in texts
        ]
        
        output_hidden_states_list = []
        
        # STEP 2: BATCH PROCESSING (for efficiency)
        # Processes multiple texts simultaneously to speed up
        for i in tqdm.tqdm(range(0, len(tokenized_texts), batch_size), desc="Traitement des textes"):
            batch = tokenized_texts[i:i + batch_size]
            
            # STEP 3: PADDING (length alignment)
            # All texts must have the same length for the batch
            # Short texts are padded with zeros
            max_len = max(t.shape[1] for t in batch)
            batch_tensors = []
            
            for tokens in batch:
                # Ajout de zéros si le texte est plus court que max_len
                if tokens.shape[1] < max_len:
                    padding = torch.zeros(1, max_len - tokens.shape[1], dtype=tokens.dtype)
                    tokens = torch.cat([tokens, padding], dim=1)
                batch_tensors.append(tokens)
            
            # Conversion en tensor PyTorch et envoi sur GPU/CPU
            batch_tensor = torch.cat(batch_tensors, dim=0).to(self.device)
            
            # STEP 4: PASS THROUGH ROERTA
            # RoBERTa model transforms tokens into vector representations
            with torch.no_grad():  # No gradient computation (inference mode)
                # Pass through RoBERTa model
                outputs = self.model(batch_tensor, output_hidden_states=True)
                # Retrieve last hidden layer (richest representation)
                hidden_states = outputs.hidden_states[-1]
                # STEP 5: POOLING (average over tokens)
                # Average all tokens to get ONE vector per text
                # Shape before: (batch_size, n_tokens, 768)
                # Shape after: (batch_size, 768)
                text_representations = hidden_states.mean(dim=1)
                # Conversion en numpy pour compatibilité avec le reste du pipeline
                text_representations = text_representations.cpu().numpy()
                
            output_hidden_states_list.append(text_representations)
        
        # CONCATENATION: Assembles all batches into a single array
        # Final result: (n_texts, 768) in float32
        # REMINDER: This data is IN CLEAR, it will be encrypted later
        return np.concatenate(output_hidden_states_list, axis=0)
    
    def process_single_text(self, text: str) -> np.ndarray:
        """
        Traite un seul texte.
        
        Args:
            text: Texte à traiter
            
        Returns:
            Array numpy de shape (1, hidden_size)
        """
        return self.text_to_tensor([text])

