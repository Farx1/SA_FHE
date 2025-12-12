'use client';

import { useState } from 'react';
import { Lock, Unlock, ArrowRight, Shield, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';

export default function FHEProcess() {
  const [expandedStep, setExpandedStep] = useState<number | null>(null);

  const steps = [
    {
      id: 1,
      title: 'Text → Vector (IN CLEAR)',
      shortDescription: 'Text converted to 768-dimensional vector using RoBERTa',
      fullDescription: 'The input text is converted to a 768-dimensional vector using RoBERTa transformer model. This step is in clear text before encryption because RoBERTa needs to process the text to understand its semantic meaning.',
      icon: <Eye className="w-6 h-6" />,
      color: 'from-orange-500 to-red-500',
      status: 'clear',
      details: 'Location: text_processor.py - text_to_tensor()',
      technicalDetails: [
        'Uses cardiffnlp/twitter-roberta-base-sentiment-latest model',
        'Tokenization: Text split into tokens (words/subwords)',
        'Encoding: Tokens converted to numeric IDs',
        'RoBERTa Processing: Pass through pre-trained model',
        'Pooling: Average of hidden states to get 768D vector',
        'Output: Float32 array of shape (1, 768)'
      ],
      codeExample: `def text_to_tensor(texts):
    # Tokenize text
    tokens = tokenizer.encode(text, max_length=512)
    # Process with RoBERTa
    outputs = model(tokens, output_hidden_states=True)
    # Extract 768D vector
    vector = outputs.hidden_states[-1].mean(dim=1)
    return vector.numpy()`
    },
    {
      id: 2,
      title: 'Quantization',
      shortDescription: 'Float values converted to integers (required for FHE)',
      fullDescription: 'Float values are converted to integers because FHE cryptographic operations can only work with integers, not floating-point numbers. Precision is reduced (typically 2-3 bits) but this is necessary for cryptographic operations.',
      icon: <ArrowRight className="w-6 h-6" />,
      color: 'from-red-500 to-orange-500',
      status: 'processing',
      details: 'Location: model_utils.py - compile_model()',
      technicalDetails: [
        'Input: Float32 values (768 dimensions)',
        'Process: Normalize to [0, 1] range',
        'Quantization: Multiply by 2^n_bits - 1',
        'Output: Integer values (typically 0-7 for n_bits=3)',
        'Example: 0.75 → 3 (if n_bits=2)',
        'Precision trade-off: Lower bits = faster FHE, less accuracy'
      ],
      codeExample: `def quantize(data, n_bits=3):
    # Normalize
    normalized = (data - min) / (max - min)
    # Quantize
    quantized = (normalized * (2**n_bits - 1)).astype(int)
    return quantized`
    },
    {
      id: 3,
      title: 'ENCRYPTION',
      shortDescription: 'Data encrypted using public key, becomes unreadable ciphertext',
      fullDescription: 'Data is encrypted using the public key generated during model compilation. The data becomes unreadable (ciphertext). The server/model cannot see the original values - only encrypted data. This is the core of FHE security.',
      icon: <Lock className="w-6 h-6" />,
      color: 'from-red-600 to-black',
      status: 'encrypted',
      details: 'Location: Automatic in client.py when FHE mode enabled',
      technicalDetails: [
        'Input: Quantized integers',
        'Key: Public key (generated during compilation)',
        'Process: Cryptographic encryption (CKKS/BFV scheme)',
        'Output: Ciphertext (encrypted data)',
        'Security: Server cannot decrypt without secret key',
        'Properties: Supports homomorphic operations'
      ],
      codeExample: `# Automatic encryption in Concrete-ML
encrypted_data = public_key.encrypt(quantized_data)
# Data is now unreadable
# Server only sees: [encrypted_ciphertext_1, ...]`
    },
    {
      id: 4,
      title: 'FHE PREDICTION',
      shortDescription: 'XGBoost processes encrypted data, all operations on ciphertext',
      fullDescription: 'The XGBoost model processes encrypted data. All operations (additions, multiplications) happen on ciphertext. The model never sees clear data - only encrypted values. This is the magic of FHE: computations on encrypted data without decryption.',
      icon: <Shield className="w-6 h-6" />,
      color: 'from-orange-600 to-red-600',
      status: 'encrypted',
      details: 'Location: client.py - model_api.predict(X)',
      technicalDetails: [
        'Input: Encrypted data (ciphertext)',
        'Operations: Additions, multiplications (homomorphic)',
        'Model: XGBoost decision trees on encrypted data',
        'Process: Each tree node operates on ciphertext',
        'Output: Encrypted prediction (still ciphertext)',
        'Key Point: Model never sees clear values!'
      ],
      codeExample: `# Model operates on encrypted data
encrypted_prediction = model.predict(encrypted_data)
# All computations happen on ciphertext
# Result is still encrypted`
    },
    {
      id: 5,
      title: 'DECRYPTION',
      shortDescription: 'Encrypted result decrypted using secret key (only client has it)',
      fullDescription: 'The encrypted result is decrypted using the secret (private) key. Only the client has the secret key. The server never had access to it. This ensures that only the client can see the final prediction result.',
      icon: <Unlock className="w-6 h-6" />,
      color: 'from-orange-500 to-red-500',
      status: 'clear',
      details: 'Location: Automatic after prediction',
      technicalDetails: [
        'Input: Encrypted prediction (ciphertext)',
        'Key: Secret key (only client has this)',
        'Process: Cryptographic decryption',
        'Output: Clear prediction (integer)',
        'Security: Only client can decrypt',
        'Final Step: Dequantization back to float if needed'
      ],
      codeExample: `# Client decrypts with secret key
clear_prediction = secret_key.decrypt(encrypted_prediction)
# Result: 0 (Negative) or 1 (Positive)
# Only client can see this!`
    },
  ];

  const toggleStep = (stepId: number) => {
    setExpandedStep(expandedStep === stepId ? null : stepId);
  };

  return (
    <section id="process" className="py-20 px-4 bg-black">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            The FHE Process
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Five critical steps that keep your data encrypted throughout processing
          </p>
          <p className="text-sm text-orange-400 mt-2">Click on any step to see detailed information</p>
        </div>

        <div className="space-y-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`relative bg-gradient-to-r ${step.color} p-[2px] rounded-xl cursor-pointer transform transition-all duration-300 ${
                expandedStep === step.id ? 'scale-105 shadow-2xl shadow-red-500/50' : 'hover:scale-102'
              }`}
              onClick={() => toggleStep(step.id)}
            >
              <div className="bg-black rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className={`flex-shrink-0 w-16 h-16 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center text-white shadow-lg`}>
                    {step.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-semibold text-gray-400">STEP {step.id}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          step.status === 'encrypted' 
                            ? 'bg-red-500/20 text-red-300 border border-red-500/30' 
                            : step.status === 'clear'
                            ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                            : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                        }`}>
                          {step.status === 'encrypted' ? '🔒 ENCRYPTED' : step.status === 'clear' ? '👁️ CLEAR' : '⚙️ PROCESSING'}
                        </span>
                      </div>
                      {expandedStep === step.id ? (
                        <ChevronUp className="w-5 h-5 text-orange-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">{step.title}</h3>
                    <p className="text-gray-300 mb-3">{step.shortDescription}</p>
                    <p className="text-sm text-gray-400 font-mono">{step.details}</p>

                    {/* Expanded Details */}
                    {expandedStep === step.id && (
                      <div className="mt-6 pt-6 border-t border-gray-800 space-y-4 animate-fadeIn">
                        <div>
                          <h4 className="text-lg font-semibold text-orange-400 mb-2">Full Description</h4>
                          <p className="text-gray-300 leading-relaxed">{step.fullDescription}</p>
                        </div>

                        <div>
                          <h4 className="text-lg font-semibold text-red-400 mb-2">Technical Details</h4>
                          <ul className="space-y-2">
                            {step.technicalDetails.map((detail, idx) => (
                              <li key={idx} className="text-gray-300 text-sm flex items-start gap-2">
                                <span className="text-orange-500 mt-1">•</span>
                                <span>{detail}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="text-lg font-semibold text-red-400 mb-2">Code Example</h4>
                          <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                            <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
                              <code>{step.codeExample}</code>
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-8">
          <h3 className="text-2xl font-bold text-white mb-4">🔑 Key Security Point</h3>
          <p className="text-lg text-gray-300">
            <span className="text-red-400 font-semibold">Data remains encrypted throughout the entire processing pipeline!</span>
            <br />
            <span className="text-gray-400 mt-2 block">
              The server/model only sees encrypted data. All computations happen on ciphertext. Only the client can decrypt the final result.
            </span>
          </p>
        </div>
      </div>
    </section>
  );
}
