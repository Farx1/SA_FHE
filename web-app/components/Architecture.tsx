'use client';

export default function Architecture() {
  const steps = [
    { id: 1, title: 'User Input', description: 'Text to analyze', icon: '📝', color: 'from-orange-500 to-red-500' },
    { id: 2, title: 'RoBERTa', description: 'Text → 768D Vector', icon: '🤖', color: 'from-red-500 to-orange-500' },
    { id: 3, title: 'Quantization', description: 'Float → Integer', icon: '🔢', color: 'from-orange-600 to-red-600' },
    { id: 4, title: 'FHE Encryption', description: 'Encrypt with public key', icon: '🔐', color: 'from-red-600 to-black' },
    { id: 5, title: 'XGBoost (FHE)', description: 'Predict on encrypted data', icon: '🧠', color: 'from-black to-red-600' },
    { id: 6, title: 'Decryption', description: 'Decrypt with secret key', icon: '🔓', color: 'from-red-500 to-orange-500' },
    { id: 7, title: 'Result', description: 'Sentiment prediction', icon: '✅', color: 'from-orange-500 to-red-500' },
  ];

  return (
    <section id="architecture" className="py-20 px-4 bg-black">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            System Architecture
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            The complete pipeline from text input to encrypted prediction
          </p>
        </div>

        <div className="relative">
          {/* Connection lines */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 opacity-30 -translate-y-1/2"></div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 relative z-10">
            {steps.map((step, index) => (
              <div key={step.id} className="flex flex-col items-center">
                <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center text-3xl mb-3 shadow-lg transform hover:scale-110 transition-all duration-300`}>
                  {step.icon}
                </div>
                <h3 className="text-sm font-semibold text-white text-center mb-1">{step.title}</h3>
                <p className="text-xs text-gray-400 text-center">{step.description}</p>
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-10 left-1/2 w-full h-0.5 bg-gradient-to-r from-purple-500/50 to-pink-500/50 transform translate-x-1/2" style={{ left: `${(index + 1) * (100 / steps.length)}%` }}></div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 bg-gray-900 rounded-xl p-8 border border-gray-800">
          <h3 className="text-2xl font-bold text-white mb-4">Key Components</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-red-300 mb-2">Text Processor</h4>
              <p className="text-gray-300 text-sm">Converts text to 768-dimensional vectors using RoBERTa transformer model</p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-orange-300 mb-2">FHE Engine</h4>
              <p className="text-gray-300 text-sm">Handles encryption, quantization, and homomorphic operations</p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-red-400 mb-2">ML Model</h4>
              <p className="text-gray-300 text-sm">XGBoost classifier trained on 2000 examples with 89% accuracy</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

