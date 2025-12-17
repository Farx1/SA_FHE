# Sentiment Analysis with Fully Homomorphic Encryption (FHE)

A project demonstrating how to perform sentiment analysis on encrypted data using Fully Homomorphic Encryption. This allows a machine learning model to process and classify text without ever seeing the original data in clear text.

## What is this project?

This project shows how to:
- Convert text into numerical vectors using RoBERTa (a transformer model)
- Train an XGBoost classifier for sentiment analysis
- Process predictions using Fully Homomorphic Encryption (FHE)
- Keep data encrypted throughout the entire computation pipeline

The end result: a sentiment analysis system that can classify text as positive or negative while the data remains encrypted during processing.

## Why FHE? Real-World Applications

Fully Homomorphic Encryption enables **privacy-preserving machine learning**: the server processes your data without ever seeing it in clear text. This has critical applications in industries where data confidentiality is paramount:

- **Healthcare**: Analyze patient feedback or medical notes for sentiment without exposing protected health information (HIPAA compliance)
- **Finance**: Process confidential client communications or internal reports while maintaining regulatory compliance (GDPR, banking secrecy)
- **Legal**: Analyze case documents or client correspondence without breaching attorney-client privilege
- **HR & Surveys**: Conduct anonymous employee satisfaction analysis where responses remain truly confidential
- **Social Media Moderation**: Detect harmful content on encrypted messages without reading private conversations

In this project, the **server never sees**: the original text, the numerical embeddings, or the final prediction result. Only encrypted data flows through the inference pipeline, ensuring end-to-end privacy.

## Technologies Used

**Backend:**
- **Python** - Main programming language
- **Flask** - REST API server
- **RoBERTa** (Transformers library) - Converts text to 768-dimensional vectors
- **XGBoost** - Machine learning model for sentiment classification
- **Concrete-ML** - Library for FHE operations (when available, falls back to simulator on Windows)

**Frontend:**
- **Next.js 16** - React framework for the web application
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library

## Installation & Setup

### Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **Trained model** (see step 1 below)

### Step 1: Train the Model (One-time setup)

First, you need to train the sentiment analysis model:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Train the model (takes a few minutes)
python train_model_simple.py

# Optional: Test the model quality
python test_model_quality.py
```

**Note**: On Windows, the project uses an FHE simulator for demonstration. The predictions are accurate, but encryption is simulated for educational purposes. For real FHE, use Docker/Linux/WSL.

This will create the model files in `models/sentiment_fhe_model/` that are required for the API.

### Step 2: Install Frontend Dependencies

The frontend dependencies will be automatically installed when you run `start.py` or `start.ps1`. 

If you want to install them manually:
```bash
cd web-app
npm install
cd ..
```

### Step 3: Launch the Application

Simply run:
```bash
# Windows (PowerShell)
.\start.ps1

# Or Linux/Mac/Windows (Python)
python start.py
```

That's it! The script will start both the API and the frontend automatically.

## Project Structure

```
.
├── start.py                        # ⭐ Main launcher script (Python)
├── start.ps1                       # ⭐ Main launcher script (PowerShell)
├── api_server.py                   # Flask API server (required for frontend)
├── train_model_simple.py          # Model training script (run once)
├── test_model_quality.py           # Model quality tests
├── text_processor.py               # Text to vector conversion (RoBERTa)
├── model_utils.py                  # FHE model utilities
├── fhe_simulator.py                # FHE simulator for Windows
├── requirements.txt                # Python dependencies
├── web-app/                        # Next.js frontend application
│   ├── app/                        # Next.js pages and API routes
│   │   ├── page.tsx               # Main landing page
│   │   └── api/analyze/route.ts   # Next.js API proxy
│   └── components/                 # React components
│       ├── Hero.tsx               # Hero section
│       ├── DemoSection.tsx        # Interactive demo
│       ├── FHEProcess.tsx         # FHE pipeline visualization
│       └── ...
└── models/                         # Trained models (created after training)
    └── sentiment_fhe_model/       # FHE model files
```

## How It Works

The process follows these steps:

1. **Text → Vector (Clear)**: Input text is converted to a 768-dimensional vector using RoBERTa
2. **Quantization**: Float values are converted to integers (required for FHE)
3. **Encryption**: Data is encrypted using a public key
4. **FHE Prediction**: The XGBoost model processes the encrypted data
5. **Decryption**: The result is decrypted using a private key

**Key Point**: The data remains encrypted throughout steps 3-5. The server/model never sees the original text or its numerical representation in clear form.

## Dataset

### Amazon Polarity Dataset

The model is trained on the **Amazon Polarity** dataset, which consists of product reviews from Amazon. This dataset was chosen because:

- **Real-world data**: Represents actual user opinions and language patterns
- **Balanced classes**: Approximately 50/50 distribution between positive and negative reviews
- **Diverse vocabulary**: Contains varied expressions and writing styles
- **Practical application**: Directly applicable to real sentiment analysis use cases

### Dataset Details

- **Source**: Amazon product reviews (via Hugging Face `datasets` library)
- **Training size**: 2000 examples
- **Train/Test split**: 80% training (1600 examples) / 20% test (400 examples)
- **Classes**: 
  - Negative (label: 0)
  - Positive (label: 1)
- **Balance**: ~50/50 distribution between classes

### Training Configuration

The model uses **XGBoost** with the following optimized hyperparameters:
- **Algorithm**: XGBoost Classifier
- **Cross-validation**: 5-fold CV for hyperparameter tuning
- **Best parameters**: 
  - `max_depth`: 3
  - `n_estimators`: 150
  - `learning_rate`: 0.2
- **Final accuracy**: 89% on test set

**Note**: If the Amazon Polarity dataset is unavailable, the training script automatically falls back to the IMDB dataset as an alternative.

## Running the Application

### Quick Start (Recommended)

Simply run one command from the project root:

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux/Mac/Windows (Python):**
```bash
python start.py
```

This single command will:
1. ✅ Check that the model is trained
2. ✅ Verify npm is installed
3. ✅ Install Next.js dependencies if needed
4. 🚀 Start the Flask API server (port 8002)
5. 🌐 Start the Next.js frontend (port 3000)

**Expected output:**
```
==============================================================
  FHE Sentiment Analysis - Démarrage
==============================================================

✓ Modèle trouvé
✓ npm détecté (version X.X.X)
✓ Dépendances Next.js déjà installées

📡 Démarrage du serveur API Flask (port 8002)...
✓ API démarrée sur http://localhost:8002

🌐 Démarrage de l'application Next.js...
✓ Next.js démarré sur http://localhost:3000

==============================================================
  ✅ Application démarrée avec succès!
==============================================================

📍 URLs disponibles:
   - Frontend: http://localhost:3000
   - API:      http://localhost:8002

💡 Appuyez sur Ctrl+C pour arrêter les serveurs
```

### Manual Start (Alternative)

If you prefer to run the servers separately:

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - Next.js Frontend:**
```bash
cd web-app
npm run dev
```

### Using the Interface

1. **Open your browser** and navigate to `http://localhost:3000`
2. **Enter text** in the textarea (e.g., "I love this product!")
3. **Click "Run inference"** to analyze the sentiment
4. **View the results**: The interface will show:
   - Sentiment prediction (Positive/Negative)
   - Confidence score
   - Processing time
   - Step-by-step FHE pipeline visualization

The frontend communicates with the Python API to perform encrypted sentiment analysis while keeping your data private.

## Model Performance

- **Accuracy**: 89% on test set (see [Dataset](#dataset) section for details)
- **Dataset**: Amazon Polarity (2000 training examples, 80/20 train/test split)
- **Processing Time**: ~2-3 seconds per prediction (including FHE overhead)
- **Classes**: Binary classification (Negative/Positive)

## Important Notes

- **FHE Simulator**: On Windows without Docker/WSL, the project uses a simulator that demonstrates the FHE process structure. Predictions are accurate, but encryption is simulated for educational purposes.
- **Model Training**: Takes a few minutes depending on your hardware. Only needs to be done once.
- **API Port**: The Flask API runs on port 8002 by default. If the port is busy, the server will show an error.
- **Frontend Port**: Next.js runs on port 3000 by default. If occupied, it will automatically use the next available port (e.g., 3001, 3002).
- **Both servers must run**: The frontend requires the API server to be running. Make sure both terminals are active.

## Requirements

**Python dependencies** (see `requirements.txt`):
- torch
- transformers
- xgboost
- numpy
- pandas
- scikit-learn
- flask
- flask-cors

**Node.js dependencies** (see `web-app/package.json`):
- next
- react
- react-dom
- tailwindcss
- framer-motion

**Note for Windows users**: 
- `concrete-ml` is not available natively on Windows, so the project automatically uses an FHE simulator
- Predictions are accurate, but encryption is simulated for educational purposes
- For real FHE, use Docker/Linux/WSL

## Future Improvements

There are several areas that could be improved:
- Support for more sentiment classes (neutral, very positive, etc.)
- Better handling of longer texts
- Optimized FHE parameters for faster processing
- Real-time encryption visualization
- Support for batch predictions

## License

This is a student project created for educational purposes.

## Contact

For questions or feedback, feel free to open an issue on GitHub.
