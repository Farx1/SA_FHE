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

- **RoBERTa** (Transformers library) - Converts text to 768-dimensional vectors
- **XGBoost** - Machine learning model for sentiment classification
- **Concrete-ML** - Library for FHE operations (when available)
- **Python** - Main programming language
- **Gradio** - Web interface for testing
- **Next.js** - Modern web application for project showcase

## Installation

### Quick Start (Windows) - Recommended

**Easiest way: Use the all-in-one script!**

```bash
# 1. Install dependencies (Windows - without concrete-ml)
pip install -r requirements.txt

# Or use the Windows-specific file (same thing):
# pip install -r requirements-windows.txt

# 2. Run everything: training → tests → launch app
python run_all.py
```

**Note**: `concrete-ml` is not available on Windows. The project automatically uses an FHE simulator for demonstration. This is normal and expected behavior.

This script will:
- Check dependencies
- Train the model (or use existing if available)
- Run quality tests
- Launch the application (Gradio or Next.js)

**Manual steps (if needed):**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python train_model_simple.py

# 3. Test the model
python test_model_quality.py

# 4. Launch the web interface
python client.py
```

The interface will be available at `http://localhost:7860` (or another port if 7860 is busy).

### For Real FHE (Docker/Linux/WSL/Google Colab)

For actual FHE encryption, you need Concrete-ML which requires a Linux environment:

**Option 1: Docker (Recommended for Windows) 🐳**

Docker allows you to run Concrete-ML on Windows without WSL:

```bash
# Windows PowerShell
.\run_docker.ps1 all

# Or Linux/Mac
chmod +x run_docker.sh
./run_docker.sh all
```

**Available Docker commands:**
```bash
# Train the model
.\run_docker.ps1 train

# Test the model
.\run_docker.ps1 test

# Launch Gradio interface
.\run_docker.ps1 gradio

# Launch Flask API
.\run_docker.ps1 api

# Open shell in container
.\run_docker.ps1 shell
```

**Prerequisites for Docker:**
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop) for Windows
- Make sure Docker is running before executing the commands

**Option 1b: Docker with MCP Tool Kit 🔌 (Advanced)**

MCP Tool Kit provides enhanced Docker management and integration with Claude Desktop:

```bash
# Windows PowerShell - Install MCP Tool Kit
.\install_mcp_toolkit.ps1

# Configure MCP server for this project
.\setup_mcp_server.ps1

# Run via MCP
.\run_mcp.ps1 all

# Or Linux/Mac
chmod +x install_mcp_toolkit.sh setup_mcp_server.sh run_mcp.sh
./install_mcp_toolkit.sh
./setup_mcp_server.sh
./run_mcp.sh all
```

**Available MCP commands:**
```bash
# Train the model
.\run_mcp.ps1 train

# Test the model
.\run_mcp.ps1 test

# Launch Gradio interface
.\run_mcp.ps1 gradio

# Launch Flask API
.\run_mcp.ps1 api

# Start MCP server mode (for Claude Desktop integration)
.\run_mcp.ps1 mcp-server
```

**MCP Tool Kit Benefits:**
- Enhanced Docker container management
- Integration with Claude Desktop
- Server mode for remote access
- Better logging and monitoring

**Option 2: Google Colab (Easiest)**
- Open `FHE_Sentiment_Analysis_Complete.ipynb` in Google Colab
- Run all cells - everything is pre-configured

**Option 3: Linux/WSL**
```bash
pip install concrete-ml
python train_model_simple.py
```

**Note**: On Windows without Docker/WSL, the project uses an FHE simulator that demonstrates the complete FHE process structure. The predictions are accurate, but the encryption is simulated for educational purposes. **Use Docker to get real FHE on Windows!**

## Project Structure

```
.
├── run_all.py                      # ⭐ All-in-one script (training → tests → launch)
├── run_docker.ps1                  # 🐳 Docker script for Windows (PowerShell)
├── run_docker.sh                    # 🐳 Docker script for Linux/Mac
├── install_mcp_toolkit.ps1         # 🔌 MCP Tool Kit installer (Windows)
├── install_mcp_toolkit.sh          # 🔌 MCP Tool Kit installer (Linux/Mac)
├── setup_mcp_server.ps1            # 🔌 MCP server configuration (Windows)
├── setup_mcp_server.sh             # 🔌 MCP server configuration (Linux/Mac)
├── run_mcp.ps1                     # 🔌 Run via MCP Tool Kit (Windows)
├── run_mcp.sh                       # 🔌 Run via MCP Tool Kit (Linux/Mac)
├── Dockerfile                       # Docker configuration
├── docker-compose.yml              # Docker Compose configuration
├── requirements-docker.txt         # Dependencies for Docker (without concrete-ml)
├── train_model_simple.py          # Main training script
├── client.py                       # Gradio web interface
├── api_server.py                   # Flask API for Next.js app
├── text_processor.py               # Text to vector conversion (RoBERTa)
├── model_utils.py                  # FHE model utilities
├── fhe_simulator.py                # FHE simulator for Windows
├── test_model.py                   # Model consistency tests
├── test_model_quality.py           # Quality tests with sample phrases
├── FHE_Sentiment_Analysis_Complete.ipynb  # Complete Colab notebook
├── requirements.txt                # Python dependencies (Windows - no concrete-ml)
├── requirements-windows.txt        # Windows-specific requirements
├── web-app/                        # Next.js showcase application
│   ├── app/                        # Next.js pages
│   └── components/                 # React components
└── models/                         # Trained models (created after training)
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

## Usage

### Quick Start (All-in-One)

The easiest way to get started:

```bash
python run_all.py
```

This single script will:
1. ✅ Check all dependencies
2. 🚀 Train the model (or use existing)
3. 🧪 Run quality tests
4. 🎨 Launch the application (choose Gradio or Next.js)

### Step-by-Step Usage

**1. Training the Model**

```bash
python train_model_simple.py
```

This will:
- Load 2000 examples from the Amazon Polarity dataset
- Train an XGBoost model with optimized hyperparameters
- Compile the model for FHE (or use simulator if Concrete-ML unavailable)
- Save the model to `models/sentiment_fhe_model/`

**Expected accuracy**: ~89% on test set

**2. Testing the Model**

Test with predefined phrases:
```bash
python test_model_quality.py
```

Or run consistency tests:
```bash
python test_model.py
```

**3. Using the Web Interface**

**Gradio Interface** (Python - Simple & Fast):
```bash
python client.py
```
Features:
- Real-time sentiment analysis
- Live statistics dashboard
- Interactive charts
- Step-by-step FHE process visualization

**Next.js Showcase** (Modern web app):
```bash
# Terminal 1: Start Python API
python api_server.py

# Terminal 2: Start Next.js app
cd web-app
npm install
npm run dev
```
Open `http://localhost:3000` for a beautiful showcase of the project.

## Model Performance

- **Accuracy**: 89% on test set (see [Dataset](#dataset) section for details)
- **Dataset**: Amazon Polarity (2000 training examples, 80/20 train/test split)
- **Processing Time**: ~2-3 seconds per prediction (including FHE overhead)
- **Classes**: Binary classification (Negative/Positive)

## Important Notes

- **FHE Simulator**: On Windows without Docker/WSL, the project uses a simulator that demonstrates the FHE process structure. Predictions are accurate, but encryption is simulated.
- **Real FHE on Windows**: Use Docker! Run `.\run_docker.ps1 all` to get real FHE encryption on Windows.
- **Real FHE on Linux**: Requires Concrete-ML which works natively on Linux/WSL or Google Colab
- **Model Training**: Takes a few minutes depending on your hardware
- **FHE Compilation**: If using real FHE, compilation can take 5-10 minutes
- **Docker**: The easiest way to get real FHE on Windows. Install Docker Desktop and use the provided scripts.

## Requirements

See `requirements.txt` for full list. Main dependencies:
- torch
- transformers
- xgboost
- gradio
- numpy
- pandas
- scikit-learn
- plotly
- flask
- flask-cors

**Note for Windows users**: 
- `concrete-ml` is commented out in `requirements.txt` because it's not available natively on Windows
- **Use Docker** (`.\run_docker.ps1`) to get real FHE on Windows
- Without Docker, the project automatically uses the FHE simulator (predictions are accurate, encryption is simulated)

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
